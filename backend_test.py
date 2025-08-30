import requests
import sys
import json
from datetime import datetime
import time

class FrageEDUAPITester:
    def __init__(self, base_url="https://frageedu-admin.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.household_token = None
        self.admin_token = None
        self.test_user_id = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if not endpoint.startswith('http') else endpoint
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        # Use admin token for admin endpoints
        if endpoint.startswith('admin/') and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'
        elif self.token and 'Authorization' not in headers:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, params=params, timeout=10)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2, default=str)}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_signup(self):
        """Test user signup with new model structure"""
        timestamp = datetime.now().strftime('%H%M%S')
        signup_data = {
            "email": f"parent{timestamp}@frage.edu",
            "phone": "010-1234-5678",
            "name": f"김학부모{timestamp}",
            "student_name": f"김학생{timestamp}",
            "password": "TestPassword123!",
            "terms_accepted": True,
            "branch": "junior"
        }
        
        success, response = self.run_test("User Signup (New Model)", "POST", "signup", 200, signup_data)
        if success and 'token' in response:
            self.token = response['token']
            self.household_token = response['household_token']
            self.test_user_id = response['user']['id']
            print(f"   Saved token: {self.token[:20]}...")
            print(f"   Saved household_token: {self.household_token}")
            print(f"   Saved user_id: {self.test_user_id}")
            return True
        return False

    def test_signup_duplicate_email(self):
        """Test signup with duplicate email"""
        signup_data = {
            "email": "test@frage.edu",  # Using same email as before
            "phone": "010-1234-5678",
            "password": "TestPassword123!",
            "terms_accepted": True
        }
        
        success, response = self.run_test("Duplicate Email Signup", "POST", "signup", 400, signup_data)
        return success

    def test_signup_no_terms(self):
        """Test signup without accepting terms"""
        timestamp = datetime.now().strftime('%H%M%S')
        signup_data = {
            "email": f"noterms{timestamp}@frage.edu",
            "phone": "010-1234-5678",
            "password": "TestPassword123!",
            "terms_accepted": False
        }
        
        success, response = self.run_test("Signup No Terms", "POST", "signup", 400, signup_data)
        return success

    def test_login(self):
        """Test user login with last_login_at update"""
        # First create a test user for login
        timestamp = datetime.now().strftime('%H%M%S')
        signup_data = {
            "email": f"logintest{timestamp}@frage.edu",
            "phone": "010-9876-5432",
            "name": f"로그인테스트{timestamp}",
            "student_name": f"학생테스트{timestamp}",
            "password": "LoginTest123!",
            "terms_accepted": True,
            "branch": "kinder"
        }
        
        # Create user first
        success, signup_response = self.run_test("Create Login Test User", "POST", "signup", 200, signup_data)
        if not success:
            return False
        
        # Now test login
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        success, response = self.run_test("User Login (Updated)", "POST", "login", 200, login_data)
        if success and 'token' in response:
            # Verify last_login_at is updated
            if 'user' in response and 'last_login_at' in response['user']:
                print(f"   ✅ Last login updated: {response['user']['last_login_at']}")
            return True
        return False

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "test@frage.edu",
            "password": "WrongPassword"
        }
        
        success, response = self.run_test("Invalid Login", "POST", "login", 401, login_data)
        return success

    def test_profile(self):
        """Test get user profile"""
        if not self.token:
            print("❌ No token available for profile test")
            return False
            
        success, response = self.run_test("Get Profile", "GET", "profile", 200)
        return success

    def test_get_admission_data(self):
        """Test get admission data"""
        if not self.household_token:
            print("❌ No household token available for admission test")
            return False
            
        success, response = self.run_test("Get Admission Data", "GET", f"admission/{self.household_token}", 200)
        return success

    def test_update_consent(self):
        """Test update consent data"""
        if not self.household_token:
            print("❌ No household token available for consent test")
            return False
            
        consent_data = {
            "regulation_agreed": True,
            "privacy_agreed": True,
            "photo_consent": True,
            "medical_consent": True
        }
        
        success, response = self.run_test("Update Consent", "PUT", f"admission/{self.household_token}/consent", 200, consent_data)
        return success

    def test_update_forms(self):
        """Test update forms data"""
        if not self.household_token:
            print("❌ No household token available for forms test")
            return False
            
        forms_data = {
            "student_name": "김테스트",
            "birth_date": "2015-03-15",
            "parent_name": "김학부모",
            "emergency_contact": "010-9876-5432",
            "allergies": "견과류 알레르기",
            "milk_program": True,
            "afterschool_program": "coding"
        }
        
        success, response = self.run_test("Update Forms", "PUT", f"admission/{self.household_token}/forms", 200, forms_data)
        return success

    def test_update_guides(self):
        """Test update guides status"""
        if not self.household_token:
            print("❌ No household token available for guides test")
            return False
            
        success, response = self.run_test("Update Guides", "PUT", f"admission/{self.household_token}/guides", 200)
        return success

    def test_update_checklist(self):
        """Test update checklist data"""
        if not self.household_token:
            print("❌ No household token available for checklist test")
            return False
            
        checklist_data = {
            "items": [
                {"id": 1, "text": "학용품 준비", "checked": True},
                {"id": 2, "text": "실내화 구입", "checked": True},
                {"id": 3, "text": "체육복 준비", "checked": False}
            ]
        }
        
        success, response = self.run_test("Update Checklist", "PUT", f"admission/{self.household_token}/checklist", 200, checklist_data)
        return success

    def test_get_admission_data_after_updates(self):
        """Test get admission data after all updates to verify persistence"""
        if not self.household_token:
            print("❌ No household token available for final admission test")
            return False
            
        success, response = self.run_test("Get Final Admission Data", "GET", f"admission/{self.household_token}", 200)
        
        if success and response:
            print("\n📊 Final Admission Status:")
            print(f"   Consent: {response.get('consent_status', 'unknown')}")
            print(f"   Forms: {response.get('forms_status', 'unknown')}")
            print(f"   Guides: {response.get('guides_status', 'unknown')}")
            print(f"   Checklist: {response.get('checklist_status', 'unknown')}")
            
            # Check if all statuses are completed
            all_completed = all([
                response.get('consent_status') == 'completed',
                response.get('forms_status') == 'completed',
                response.get('guides_status') == 'completed',
                response.get('checklist_status') == 'completed'
            ])
            
            if all_completed:
                print("✅ All sections completed successfully!")
            else:
                print("⚠️  Some sections not completed")
        
        return success

    # Admin Authentication Tests
    def test_admin_signup(self):
        """Test admin account creation"""
        timestamp = datetime.now().strftime('%H%M%S')
        admin_data = {
            "username": f"admin{timestamp}",
            "email": f"admin{timestamp}@frage.edu",
            "password": "AdminPass123!"
        }
        
        success, response = self.run_test("Admin Signup", "POST", "admin/signup", 200, admin_data)
        if success and 'token' in response:
            self.admin_token = response['token']
            print(f"   Saved admin token: {self.admin_token[:20]}...")
            return True
        return False

    def test_admin_login(self):
        """Test admin login"""
        # Create admin first if not exists
        if not self.admin_token:
            if not self.test_admin_signup():
                return False
        
        # Test login with existing admin
        timestamp = datetime.now().strftime('%H%M%S')
        admin_data = {
            "username": f"loginadmin{timestamp}",
            "email": f"loginadmin{timestamp}@frage.edu", 
            "password": "AdminLogin123!"
        }
        
        # Create admin for login test
        success, signup_response = self.run_test("Create Admin for Login", "POST", "admin/signup", 200, admin_data)
        if not success:
            return False
        
        # Test login
        login_data = {
            "username": admin_data["username"],
            "password": admin_data["password"]
        }
        
        success, response = self.run_test("Admin Login", "POST", "admin/login", 200, login_data)
        return success

    # Member Management Tests
    def test_get_members_list(self):
        """Test GET /admin/members with various filters"""
        if not self.admin_token:
            print("❌ No admin token available for members list test")
            return False
        
        # Test basic list
        success, response = self.run_test("Get Members List", "GET", "admin/members", 200)
        if not success:
            return False
        
        # Test with search query
        params = {"query": "김"}
        success, response = self.run_test("Get Members with Search", "GET", "admin/members", 200, params=params)
        if not success:
            return False
        
        # Test with branch filter
        params = {"branch": "junior"}
        success, response = self.run_test("Get Members by Branch", "GET", "admin/members", 200, params=params)
        if not success:
            return False
        
        # Test with status filter
        params = {"status": "active"}
        success, response = self.run_test("Get Active Members", "GET", "admin/members", 200, params=params)
        if not success:
            return False
        
        # Test with pagination
        params = {"page": 1, "pageSize": 10}
        success, response = self.run_test("Get Members with Pagination", "GET", "admin/members", 200, params=params)
        if not success:
            return False
        
        # Test with sorting
        params = {"sort": "joinedAt:desc"}
        success, response = self.run_test("Get Members Sorted", "GET", "admin/members", 200, params=params)
        
        return success

    def test_get_member_details(self):
        """Test GET /admin/members/:id for detailed member profile"""
        if not self.admin_token or not self.test_user_id:
            print("❌ No admin token or test user ID available for member details test")
            return False
        
        success, response = self.run_test("Get Member Details", "GET", f"admin/members/{self.test_user_id}", 200)
        
        if success and response:
            # Verify response structure
            required_fields = ['user', 'parent', 'students']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            print("✅ Member details structure verified")
        
        return success

    def test_reset_member_password(self):
        """Test POST /admin/members/:id/reset-password with audit logging"""
        if not self.admin_token or not self.test_user_id:
            print("❌ No admin token or test user ID available for password reset test")
            return False
        
        success, response = self.run_test("Reset Member Password", "POST", f"admin/members/{self.test_user_id}/reset-password", 200)
        
        if success and response:
            if 'temporary_password' in response:
                print(f"✅ Temporary password generated: {response['temporary_password']}")
            else:
                print("⚠️ No temporary password in response")
        
        return success

    def test_update_member_status(self):
        """Test PATCH /admin/members/:id/status for enable/disable with audit"""
        if not self.admin_token or not self.test_user_id:
            print("❌ No admin token or test user ID available for status update test")
            return False
        
        # Test disable user
        status_data = {"status": "disabled"}
        success, response = self.run_test("Disable Member", "PATCH", f"admin/members/{self.test_user_id}/status", 200, status_data)
        if not success:
            return False
        
        # Test enable user
        status_data = {"status": "active"}
        success, response = self.run_test("Enable Member", "PATCH", f"admin/members/{self.test_user_id}/status", 200, status_data)
        
        return success

    def test_bulk_export_members(self):
        """Test POST /admin/members/bulk/export for CSV export"""
        if not self.admin_token or not self.test_user_id:
            print("❌ No admin token or test user ID available for bulk export test")
            return False
        
        export_data = [self.test_user_id]
        success, response = self.run_test("Bulk Export Members", "POST", "admin/members/bulk/export", 200, export_data)
        
        if success and response:
            if 'csv_content' in response:
                print("✅ CSV content generated successfully")
                # Print first few lines of CSV for verification
                csv_lines = response['csv_content'].split('\n')[:3]
                for line in csv_lines:
                    print(f"   CSV: {line}")
            else:
                print("⚠️ No CSV content in response")
        
        return success

    def test_bulk_notify_members(self):
        """Test POST /admin/members/bulk/notify for AlimTalk notifications"""
        if not self.admin_token or not self.test_user_id:
            print("❌ No admin token or test user ID available for bulk notify test")
            return False
        
        notify_data = {
            "user_ids": [self.test_user_id],
            "message": "테스트 알림 메시지입니다."
        }
        
        # The endpoint expects user_ids as a list in the request body
        success, response = self.run_test("Bulk Notify Members", "POST", "admin/members/bulk/notify", 200, notify_data)
        
        return success

    def test_get_audit_logs(self):
        """Test GET /admin/audit for audit log viewing"""
        if not self.admin_token:
            print("❌ No admin token available for audit logs test")
            return False
        
        # Test basic audit logs
        success, response = self.run_test("Get Audit Logs", "GET", "admin/audit", 200)
        if not success:
            return False
        
        # Test with targetId filter
        if self.test_user_id:
            params = {"targetId": self.test_user_id}
            success, response = self.run_test("Get Audit Logs by Target", "GET", "admin/audit", 200, params=params)
            if not success:
                return False
        
        # Test with action type filter
        params = {"type": "RESET_PW"}
        success, response = self.run_test("Get Audit Logs by Action", "GET", "admin/audit", 200, params=params)
        if not success:
            return False
        
        # Test with pagination
        params = {"page": 1, "limit": 10}
        success, response = self.run_test("Get Audit Logs with Pagination", "GET", "admin/audit", 200, params=params)
        
        return success

    def test_login_disabled_user(self):
        """Test login with disabled user account"""
        # First create a user and disable them
        timestamp = datetime.now().strftime('%H%M%S')
        signup_data = {
            "email": f"disabled{timestamp}@frage.edu",
            "phone": "010-5555-5555",
            "name": f"비활성사용자{timestamp}",
            "student_name": f"비활성학생{timestamp}",
            "password": "DisabledTest123!",
            "terms_accepted": True,
            "branch": "middle"
        }
        
        # Create user
        success, signup_response = self.run_test("Create User for Disable Test", "POST", "signup", 200, signup_data)
        if not success:
            return False
        
        user_id = signup_response['user']['id']
        
        # Disable the user
        if self.admin_token:
            status_data = {"status": "disabled"}
            success, response = self.run_test("Disable Test User", "PATCH", f"admin/members/{user_id}/status", 200, status_data)
            if not success:
                return False
        
        # Try to login with disabled user
        login_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        
        success, response = self.run_test("Login Disabled User", "POST", "login", 401, login_data)
        return success

def main():
    print("🚀 Starting Frage EDU API Tests")
    print("=" * 50)
    
    tester = FrageEDUAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("User Signup", tester.test_signup),
        ("Duplicate Email Signup", tester.test_signup_duplicate_email),
        ("Signup No Terms", tester.test_signup_no_terms),
        ("User Login", tester.test_login),
        ("Invalid Login", tester.test_login_invalid_credentials),
        ("Get Profile", tester.test_profile),
        ("Get Admission Data", tester.test_get_admission_data),
        ("Update Consent", tester.test_update_consent),
        ("Update Forms", tester.test_update_forms),
        ("Update Guides", tester.test_update_guides),
        ("Update Checklist", tester.test_update_checklist),
        ("Final Admission Data", tester.test_get_admission_data_after_updates)
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} crashed: {str(e)}")
            failed_tests.append(test_name)
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print("\n✅ All tests passed!")
    
    print(f"\n🔑 Test Tokens:")
    print(f"   JWT Token: {tester.token[:30] if tester.token else 'None'}...")
    print(f"   Household Token: {tester.household_token or 'None'}")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())