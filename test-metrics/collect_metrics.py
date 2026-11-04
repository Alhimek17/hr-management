#!/usr/bin/env python3
"""Сбор метрик качества для лабораторной работы №5."""
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "metrics.json"
OUT_MD = ROOT / "metrics-report.md"
PIPELINE_START = Path(__file__).resolve().parent / ".pipeline-start"

def read_eslint():
    path = ROOT / "frontend" / "eslint-report.json"
    if not path.exists():
        return 0, 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return 0, 0
    errors = sum(f.get("errorCount", 0) for f in data)
    warnings = sum(f.get("warningCount", 0) for f in data)
    return errors, warnings

def read_cobertura(path):
    if not path.exists():
        return 0, 0
    try:
        tree = ET.parse(path)
    except Exception:
        return 0, 0
    root = tree.getroot()
    lv = int(float(root.attrib.get("lines-valid", 0)))
    lc = int(float(root.attrib.get("lines-covered", 0)))
    if lv == 0:
        all_lines = root.findall(".//line")
        lv = len(all_lines)
        lc = sum(1 for l in all_lines if int(l.attrib.get("hits", 0)) > 0)
    return lv, lc

def read_trx():
    # Ищем любой .trx файл в TestResults
    trx_files = list((ROOT / "TestResults").glob("**/*.trx"))
    if not trx_files:
        return 0, 0
    path = trx_files[0]
    try:
        tree = ET.parse(path)
    except Exception:
        return 0, 0
    ns = {"t": "http://microsoft.com/schemas/VisualStudio/TeamTest/2010"}
    counters = tree.getroot().find(".//t:ResultSummary/t:Counters", ns)
    if counters is None:
        return 0, 0
    passed = int(counters.attrib.get("passed", 0))
    failed = int(counters.attrib.get("failed", 0))
    return passed, failed

def git_commits_last_7_days():
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    try:
        out = subprocess.check_output(
            ["git", "log", f"--since={since}", "--pretty=format:%H|%ad", "--date=iso"],
            cwd=ROOT, text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return 0, 0.0
    if not out:
        return 0, 0.0
    lines = out.splitlines()
    count = len(lines)
    total_changed = 0
    for h in [l.split("|")[0] for l in lines]:
        try:
            stat = subprocess.check_output(
                ["git", "show", "--numstat", "--format=", h], cwd=ROOT, text=True
            )
        except subprocess.CalledProcessError:
            continue
        for row in stat.strip().splitlines():
            parts = row.split("\t")
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                total_changed += int(parts[0]) + int(parts[1])
    avg = total_changed / count if count else 0.0
    return count, avg

def pipeline_duration_seconds():
    if not PIPELINE_START.exists():
        return 0
    try:
        start = float(PIPELINE_START.read_text().strip())
    except Exception:
        return 0
    return int(datetime.now(timezone.utc).timestamp() - start)

def main():
    errors, warnings = read_eslint()

    fe_valid, fe_cov = read_cobertura(ROOT / "frontend" / "coverage" / "cobertura-coverage.xml")
    be_valid, be_cov = read_cobertura(
        next((ROOT / "TestResults").glob("**/coverage.cobertura.xml"), Path("/nonexistent"))
    )
    total_valid = fe_valid + be_valid
    total_cov = fe_cov + be_cov
    coverage_pct = round(total_cov / total_valid * 100, 2) if total_valid else 0.0

    passed, failed = read_trx()
    commits, avg_size = git_commits_last_7_days()
    duration = pipeline_duration_seconds()

    metrics = {
        "lint_errors": errors,
        "lint_warnings": warnings,
        "coverage_percent": coverage_pct,
        "tests_passed": passed,
        "tests_failed": failed,
        "commits_last_7_days": commits,
        "avg_commit_size_lines": round(avg_size, 1),
        "pipeline_duration_seconds": duration,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    OUT_JSON.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Отчёт по метрикам CI", "", f"Сгенерировано: {metrics['generated_at']}", "",
          "| № | Метрика | Значение |", "|---|---------|----------|",
          f"| 1 | Ошибки линтера | {errors} |",
          f"| 2 | Предупреждения линтера | {warnings} |",
          f"| 3 | Покрытие тестами, % | {coverage_pct} |",
          f"| 4 | Тесты пройдено / упало | {passed} / {failed} |",
          f"| 5 | Коммитов за 7 дней | {commits} |",
          f"| 6 | Средний размер коммита, строк | {round(avg_size, 1)} |",
          f"| 7 | Время пайплайна, сек | {duration} |", ""]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()