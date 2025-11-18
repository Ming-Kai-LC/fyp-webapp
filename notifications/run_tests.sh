#!/bin/bash
# Test runner script for notification system

echo "================================="
echo "Notification System Test Suite"
echo "================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running all notification tests...${NC}"
echo ""

# Run all tests
python manage.py test notifications --verbosity=2

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "Test Summary:"
    echo "- Model tests: NotificationTemplate, Notification, NotificationPreference, NotificationLog"
    echo "- Service tests: NotificationService, NotificationScheduler"
    echo "- View tests: List, Mark Read, Preferences, APIs"
    echo "- Form tests: NotificationPreferenceForm"
    echo ""
    echo "Total: 65 test methods"
else
    echo ""
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi
