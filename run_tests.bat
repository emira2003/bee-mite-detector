@echo off
echo Running UI tests for Bee Colony Health Monitor...
echo ================================================

:: Run all UI tests with verbose output
python -m pytest tests\ui -v

:: Generate coverage report if pytest-cov is installed
echo.
echo Generating coverage report...
python -m pytest tests\ui --cov=app --cov-report=term

echo.
echo Tests completed. Press any key to exit.
pause