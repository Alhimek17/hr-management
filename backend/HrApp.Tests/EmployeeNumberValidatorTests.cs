using HrApp.Api.Services;
using Xunit;

namespace HrApp.Tests;

public class EmployeeNumberValidatorTests
{
    [Theory]
    [InlineData("1234", true)]
    [InlineData("12345678", true)]
    [InlineData("123", false)]
    [InlineData("0123456", false)]
    [InlineData("123456789", false)]
    [InlineData("12a4", false)]
    [InlineData(null, false)]
    [InlineData("", false)]
    public void IsValid_ReturnsExpected(string? input, bool expected)
    {
        Assert.Equal(expected, EmployeeNumberValidator.IsValid(input));
    }
}