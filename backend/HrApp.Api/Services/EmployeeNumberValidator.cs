namespace HrApp.Api.Services;

public static class EmployeeNumberValidator
{
    // Табельный номер: от 4 до 8 цифр, не начинается с 0
    public static bool IsValid(string? number)
    {
        if (string.IsNullOrWhiteSpace(number)) return false;
        if (number.Length < 4 || number.Length > 8) return false;
        if (number[0] == '0') return false;
        return number.All(char.IsDigit);
    }
}