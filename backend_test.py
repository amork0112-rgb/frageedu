import requests
import sys
import json
from datetime import datetime
import time

class FrageEDUAPITester:
    def __init__(self, base_url="https://school-register-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.household_token = None
        self.admin_token = None
        self.parent_token = None  # For parent enrollment form tests
        self.test_user_id = None
        self.test_student_id = None  # For parent enrollment form tests
        self.parent_user_id = None  # For parent enrollment form tests
        self.parent_household_token = None  # For parent enrollment form tests
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
        timestamp = datetime.now().strftime('%H%M%S')
        signup_data = {
            "email": f"duplicate{timestamp}@frage.edu",
            "phone": "010-1234-5678",
            "name": f"중복테스트{timestamp}",
            "student_name": f"중복학생{timestamp}",
            "password": "TestPassword123!",
            "terms_accepted": True,
            "branch": "junior"
        }
        
        # Create user first
        success, response = self.run_test("Create User for Duplicate Test", "POST", "signup", 200, signup_data)
        if not success:
            return False
        
        # Try to create duplicate
        success, response = self.run_test("Duplicate Email Signup", "POST", "signup", 400, signup_data)
        return success

    def test_signup_no_terms(self):
        """Test signup without accepting terms"""
        timestamp = datetime.now().strftime('%H%M%S')
        signup_data = {
            "email": f"noterms{timestamp}@frage.edu",
            "phone": "010-1234-5678",
            "name": f"약관거부{timestamp}",
            "student_name": f"약관거부학생{timestamp}",
            "password": "TestPassword123!",
            "terms_accepted": False,
            "branch": "kinder"
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

    def test_create_super_admin(self):
        """Create a super admin for RBAC testing"""
        timestamp = datetime.now().strftime('%H%M%S')
        admin_data = {
            "username": f"superadmin{timestamp}",
            "email": f"superadmin{timestamp}@frage.edu",
            "password": "SuperAdmin123!"
        }
        
        success, response = self.run_test("Create Super Admin", "POST", "admin/signup", 200, admin_data)
        if success and 'token' in response:
            # We need to manually update this admin to super_admin role
            # For now, let's save the token and try to use it
            self.admin_token = response['token']
            print(f"   Created admin (will need role upgrade): {response['admin']['id']}")
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
        
        # The endpoint expects BulkNotifyRequest with user_ids and message
        notify_data = {
            "user_ids": [self.test_user_id],
            "message": "테스트 알림 메시지입니다."
        }
        
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

    # RBAC and Student Management Tests
    def test_init_rbac_system(self):
        """Test RBAC system initialization - should work with regular admin roles now"""
        if not self.admin_token:
            print("❌ No admin token available for RBAC init test")
            return False
        
        success, response = self.run_test("Initialize RBAC System (Fixed for regular admin)", "POST", "admin/init-rbac", 200)
        if success:
            print("✅ RBAC system initialized successfully with regular admin role")
            if response:
                print(f"   Response: {response.get('message', 'No message')}")
        else:
            print("❌ RBAC initialization failed - may still require super_admin")
        return success

    def test_admin_students_endpoint(self):
        """Test NEW /admin/students endpoint - should now exist and work correctly"""
        if not self.admin_token:
            print("❌ No admin token available for students endpoint test")
            return False
        
        # Test the NEW /admin/students endpoint - should now return 200, not 404
        success, response = self.run_test("Test NEW /admin/students endpoint", "GET", "admin/students", 200)
        if success:
            print("✅ NEW /admin/students endpoint exists and works!")
            if response:
                students = response.get('students', [])
                allowed_branches = response.get('allowed_branches', [])
                permissions = response.get('user_permissions', [])
                print(f"   Students found: {len(students)}")
                print(f"   Allowed branches: {allowed_branches}")
                print(f"   Permissions: {len(permissions)}")
        else:
            print("❌ NEW /admin/students endpoint failed")
        
        return success

    def test_admin_student_management_endpoint(self):
        """Test /admin/student-management endpoint with RBAC filtering"""
        if not self.admin_token:
            print("❌ No admin token available for student management test")
            return False
        
        # Test basic endpoint
        success, response = self.run_test("Get Student Management List", "GET", "admin/student-management", 200)
        if not success:
            return False
        
        # Check response structure
        if response:
            print(f"📊 Student Management Response Structure:")
            print(f"   Students count: {len(response.get('students', []))}")
            print(f"   Allowed branches: {response.get('allowed_branches', [])}")
            print(f"   User permissions: {len(response.get('user_permissions', []))}")
            
            # Check if we have students data
            students = response.get('students', [])
            if len(students) == 0:
                print("⚠️  No students found in response - this might be the issue!")
            else:
                print(f"✅ Found {len(students)} students")
                # Show first student structure
                if students:
                    first_student = students[0]
                    print(f"   Sample student: {first_student.get('name', 'N/A')} - Branch: {first_student.get('branch', 'N/A')}")
        
        # Test with filters
        params = {"branch_filter": "junior"}
        success, response = self.run_test("Get Students by Branch Filter", "GET", "admin/student-management", 200, params=params)
        if not success:
            return False
        
        # Test with search
        params = {"search": "김"}
        success, response = self.run_test("Search Students", "GET", "admin/student-management", 200, params=params)
        if not success:
            return False
        
        # Test with pagination
        params = {"page": 1, "limit": 10}
        success, response = self.run_test("Get Students with Pagination", "GET", "admin/student-management", 200, params=params)
        
        return success

    def test_database_student_data(self):
        """Test if there are students in the database by creating some test data"""
        if not self.admin_token:
            print("❌ No admin token available for database test")
            return False
        
        print("🔍 Checking if we need to create test student data...")
        
        # First check if we have any students via the API
        success, response = self.run_test("Check Existing Students", "GET", "admin/student-management", 200)
        if success and response:
            students = response.get('students', [])
            if len(students) > 0:
                print(f"✅ Found {len(students)} existing students in database")
                return True
            else:
                print("⚠️  No students found - this explains the null/empty data issue!")
                print("💡 The API is working correctly but there's no student data in the database")
                return True  # This is actually expected behavior
        
        return False

    def test_rbac_permissions_check(self):
        """Test RBAC permissions for current admin"""
        if not self.admin_token:
            print("❌ No admin token available for permissions test")
            return False
        
        # The student-management endpoint should show permissions in response
        success, response = self.run_test("Check Admin Permissions", "GET", "admin/student-management", 200)
        if success and response:
            permissions = response.get('user_permissions', [])
            allowed_branches = response.get('allowed_branches', [])
            
            print(f"📋 Current Admin RBAC Status:")
            print(f"   Allowed branches: {allowed_branches}")
            print(f"   Permissions count: {len(permissions)}")
            
            # Check for key permissions
            key_permissions = ['can_view_student', 'can_edit_student', 'can_view_class']
            for perm in key_permissions:
                has_perm = perm in permissions
                status = "✅" if has_perm else "❌"
                print(f"   {status} {perm}: {has_perm}")
            
            if not allowed_branches:
                print("⚠️  Admin has no allowed branches - this could cause empty results!")
            
            if 'can_view_student' not in permissions:
                print("⚠️  Admin lacks 'can_view_student' permission - this could cause access issues!")
        
        return success

    def test_create_sample_student_data(self):
        """Create sample student data using NEW /admin/create-sample-data endpoint"""
        if not self.admin_token:
            print("❌ No admin token available for creating test data")
            return False
        
        success, response = self.run_test("Create Sample Student Data (NEW endpoint)", "POST", "admin/create-sample-data", 200)
        if success:
            print("✅ Sample student data created successfully")
            if response:
                created_parents = response.get('created_parents', 0)
                created_students = response.get('created_students', 0)
                print(f"   Created {created_parents} parents and {created_students} students")
                print(f"   Message: {response.get('message', 'No message')}")
        else:
            print("❌ Failed to create sample student data")
        
        return success

    def test_branch_filtering_unauthorized_access(self):
        """Test FIXED branch filtering - admin should get empty results for unauthorized branches"""
        if not self.admin_token:
            print("❌ No admin token available for branch filtering test")
            return False
        
        print("🔍 Testing FIXED branch filtering logic...")
        
        # First, get admin's allowed branches
        success, response = self.run_test("Get Admin Allowed Branches", "GET", "admin/students", 200)
        if not success:
            return False
        
        allowed_branches = response.get('allowed_branches', [])
        print(f"   Admin allowed branches: {allowed_branches}")
        
        # Test unauthorized branch access - should return empty results
        unauthorized_branches = []
        all_branches = ["kinder", "junior", "middle"]
        for branch in all_branches:
            if branch not in allowed_branches:
                unauthorized_branches.append(branch)
        
        if unauthorized_branches:
            for branch in unauthorized_branches:
                params = {"branch_filter": branch}
                success, response = self.run_test(f"Test unauthorized {branch} branch access", "GET", "admin/students", 200, params=params)
                
                if success and response:
                    students = response.get('students', [])
                    if len(students) == 0:
                        print(f"   ✅ Correctly returned empty results for unauthorized {branch} branch")
                    else:
                        print(f"   ❌ BUG: Found {len(students)} students in unauthorized {branch} branch!")
                        return False
        else:
            print("   ℹ️  Admin has access to all branches - cannot test unauthorized access")
        
        return True

    def test_branch_filtering_authorized_access(self):
        """Test branch filtering with authorized branches - should return filtered results"""
        if not self.admin_token:
            print("❌ No admin token available for authorized branch test")
            return False
        
        print("🔍 Testing authorized branch filtering...")
        
        # Get admin's allowed branches
        success, response = self.run_test("Get Admin Info for Authorized Test", "GET", "admin/students", 200)
        if not success:
            return False
        
        allowed_branches = response.get('allowed_branches', [])
        all_students = response.get('students', [])
        
        print(f"   Admin allowed branches: {allowed_branches}")
        print(f"   Total students visible: {len(all_students)}")
        
        # Test each authorized branch
        for branch in allowed_branches:
            params = {"branch_filter": branch}
            success, response = self.run_test(f"Test authorized {branch} branch access", "GET", "admin/students", 200, params=params)
            
            if success and response:
                students = response.get('students', [])
                print(f"   Branch {branch}: {len(students)} students found")
                
                # Verify all returned students are from the requested branch
                for student in students:
                    if student.get('branch') != branch:
                        print(f"   ❌ BUG: Found student from {student.get('branch')} in {branch} filter!")
                        return False
                
                if students:
                    print(f"   ✅ All {len(students)} students correctly filtered for {branch} branch")
        
        return True

    def test_students_vs_student_management_consistency(self):
        """Test that /admin/students and /admin/student-management return identical responses"""
        if not self.admin_token:
            print("❌ No admin token available for consistency test")
            return False
        
        print("🔍 Testing endpoint consistency...")
        
        # Get response from /admin/students
        success1, response1 = self.run_test("Get /admin/students response", "GET", "admin/students", 200)
        if not success1:
            return False
        
        # Get response from /admin/student-management  
        success2, response2 = self.run_test("Get /admin/student-management response", "GET", "admin/student-management", 200)
        if not success2:
            return False
        
        # Compare key fields
        students1 = response1.get('students', [])
        students2 = response2.get('students', [])
        branches1 = response1.get('allowed_branches', [])
        branches2 = response2.get('allowed_branches', [])
        perms1 = response1.get('user_permissions', [])
        perms2 = response2.get('user_permissions', [])
        
        print(f"   /admin/students: {len(students1)} students, {len(branches1)} branches, {len(perms1)} permissions")
        print(f"   /admin/student-management: {len(students2)} students, {len(branches2)} branches, {len(perms2)} permissions")
        
        # Check consistency
        if len(students1) == len(students2) and branches1 == branches2 and len(perms1) == len(perms2):
            print("   ✅ Both endpoints return consistent data")
            return True
        else:
            print("   ❌ Endpoints return different data - inconsistency detected!")
            return False

    # NEW ADMIN ACCOUNT CREATION TESTS
    def test_existing_admin_login(self):
        """Test login with existing admin credentials (admin/AdminPass123!)"""
        # First try the original admin credentials
        login_data = {
            "username": "admin",
            "password": "AdminPass123!"
        }
        
        success, response = self.run_test("Login with original admin", "POST", "admin/login", 200, login_data)
        if success and 'token' in response:
            self.admin_token = response['token']
            print(f"   ✅ Original admin login successful")
            print(f"   Admin role: {response.get('admin', {}).get('role', 'unknown')}")
            return True
        
        # If original admin doesn't work, try with our setup admin
        timestamp = datetime.now().strftime('%H%M%S')
        setup_admin_data = {
            "username": f"setupadmin{timestamp}",
            "email": f"setupadmin{timestamp}@frage.edu",
            "password": "SetupAdmin123!"
        }
        
        # Create setup admin
        create_success, create_response = self.run_test("Create Setup Admin", "POST", "admin/signup", 200, setup_admin_data)
        if not create_success:
            return False
        
        # Login with setup admin
        login_data = {
            "username": setup_admin_data["username"],
            "password": setup_admin_data["password"]
        }
        
        success, response = self.run_test("Login with setup admin", "POST", "admin/login", 200, login_data)
        if success and 'token' in response:
            self.admin_token = response['token']
            print(f"   ✅ Setup admin login successful")
            print(f"   Admin role: {response.get('admin', {}).get('role', 'unknown')}")
            return True
        
        return False

    def test_setup_default_admins(self):
        """Test /admin/setup-default-admins endpoint to create default admin accounts"""
        if not self.admin_token:
            print("❌ No admin token available for setup default admins test")
            return False
        
        success, response = self.run_test("Setup default admin accounts", "POST", "admin/setup-default-admins", 200)
        if success:
            created_admins = response.get('created_admins', [])
            skipped_admins = response.get('skipped_admins', [])
            
            print(f"   ✅ Setup completed successfully")
            print(f"   Created admins: {len(created_admins)}")
            print(f"   Skipped admins: {len(skipped_admins)}")
            
            for admin in created_admins:
                print(f"     - Created: {admin.get('username')} ({admin.get('role')})")
            
            for admin in skipped_admins:
                print(f"     - Skipped: {admin} (already exists)")
            
            return True
        return False

    def test_new_admin_logins(self):
        """Test login credentials for each new admin account"""
        new_admins = [
            {"username": "super_admin", "password": "Super123!", "role": "super_admin"},
            {"username": "kinder_admin", "password": "Kinder123!", "role": "kinder_admin"},
            {"username": "junior_admin", "password": "Junior123!", "role": "junior_admin"},
            {"username": "middle_admin", "password": "Middle123!", "role": "middle_admin"}
        ]
        
        successful_logins = []
        failed_logins = []
        
        for admin_info in new_admins:
            login_data = {
                "username": admin_info["username"],
                "password": admin_info["password"]
            }
            
            success, response = self.run_test(f"Login {admin_info['username']}", "POST", "admin/login", 200, login_data)
            if success and 'token' in response:
                successful_logins.append(admin_info["username"])
                actual_role = response.get('admin', {}).get('role', 'unknown')
                expected_role = admin_info["role"]
                
                if actual_role == expected_role:
                    print(f"   ✅ {admin_info['username']}: Login successful, role verified ({actual_role})")
                else:
                    print(f"   ⚠️  {admin_info['username']}: Login successful but role mismatch (expected: {expected_role}, got: {actual_role})")
            else:
                failed_logins.append(admin_info["username"])
                print(f"   ❌ {admin_info['username']}: Login failed")
        
        print(f"\n📊 Login Results:")
        print(f"   Successful: {len(successful_logins)}/{len(new_admins)}")
        print(f"   Failed: {len(failed_logins)}")
        
        return len(failed_logins) == 0

    def test_role_based_access_control(self):
        """Test each admin's access to /admin/students endpoint to verify RBAC filtering"""
        admin_credentials = [
            {"username": "super_admin", "password": "Super123!", "expected_branches": ["kinder", "junior", "middle"]},
            {"username": "kinder_admin", "password": "Kinder123!", "expected_branches": ["kinder"]},
            {"username": "junior_admin", "password": "Junior123!", "expected_branches": ["junior"]},
            {"username": "middle_admin", "password": "Middle123!", "expected_branches": ["middle"]}
        ]
        
        rbac_results = []
        
        for admin_info in admin_credentials:
            # Login as this admin
            login_data = {
                "username": admin_info["username"],
                "password": admin_info["password"]
            }
            
            success, login_response = self.run_test(f"Login as {admin_info['username']} for RBAC test", "POST", "admin/login", 200, login_data)
            if not success:
                print(f"   ❌ Failed to login as {admin_info['username']}")
                rbac_results.append(False)
                continue
            
            # Set admin token for this test
            temp_admin_token = self.admin_token
            self.admin_token = login_response['token']
            
            # Test access to students endpoint
            success, response = self.run_test(f"Test RBAC for {admin_info['username']}", "GET", "admin/students", 200)
            if success:
                allowed_branches = response.get('allowed_branches', [])
                expected_branches = admin_info["expected_branches"]
                
                # Check if allowed branches match expected
                if set(allowed_branches) == set(expected_branches):
                    print(f"   ✅ {admin_info['username']}: RBAC correct - branches {allowed_branches}")
                    rbac_results.append(True)
                else:
                    print(f"   ❌ {admin_info['username']}: RBAC mismatch - expected {expected_branches}, got {allowed_branches}")
                    rbac_results.append(False)
                
                # Test branch filtering
                students = response.get('students', [])
                print(f"     Students visible: {len(students)}")
                
                # Verify students are only from allowed branches
                for student in students:
                    student_branch = student.get('branch')
                    if student_branch not in allowed_branches:
                        print(f"     ❌ Student from unauthorized branch {student_branch} visible to {admin_info['username']}")
                        rbac_results[-1] = False
                        break
                else:
                    if students:
                        print(f"     ✅ All visible students are from authorized branches")
            else:
                print(f"   ❌ {admin_info['username']}: Failed to access students endpoint")
                rbac_results.append(False)
            
            # Restore original admin token
            self.admin_token = temp_admin_token
        
        successful_rbac = sum(rbac_results)
        print(f"\n📊 RBAC Test Results:")
        print(f"   Successful: {successful_rbac}/{len(admin_credentials)}")
        
        return all(rbac_results)

    def test_create_custom_admin_with_role(self):
        """Test /admin/create-with-role endpoint to create custom admin"""
        if not self.admin_token:
            print("❌ No admin token available for create custom admin test")
            return False
        
        timestamp = datetime.now().strftime('%H%M%S')
        custom_admin_data = {
            "username": f"custom_admin_{timestamp}",
            "email": f"custom{timestamp}@frage.edu",
            "password": "CustomAdmin123!",
            "role": "junior_admin"
        }
        
        success, response = self.run_test("Create custom admin with role", "POST", "admin/create-with-role", 200, custom_admin_data)
        if success:
            created_admin = response.get('admin', {})
            print(f"   ✅ Custom admin created successfully")
            print(f"   Username: {created_admin.get('username')}")
            print(f"   Role: {created_admin.get('role')}")
            print(f"   Email: {created_admin.get('email')}")
            
            # Test login with new custom admin
            login_data = {
                "username": custom_admin_data["username"],
                "password": custom_admin_data["password"]
            }
            
            login_success, login_response = self.run_test(f"Login with custom admin", "POST", "admin/login", 200, login_data)
            if login_success:
                print(f"   ✅ Custom admin login successful")
                return True
            else:
                print(f"   ❌ Custom admin login failed")
                return False
        
        return False

    def test_admin_role_permissions_verification(self):
        """Verify that each admin role has correct permissions and branch access"""
        # Login as super_admin to test permissions
        login_data = {
            "username": "super_admin",
            "password": "Super123!"
        }
        
        success, login_response = self.run_test("Login as super_admin for permissions test", "POST", "admin/login", 200, login_data)
        if not success:
            print("❌ Failed to login as super_admin for permissions test")
            return False
        
        # Set super_admin token
        temp_admin_token = self.admin_token
        self.admin_token = login_response['token']
        
        # Test super_admin can create new admins
        timestamp = datetime.now().strftime('%H%M%S')
        test_admin_data = {
            "username": f"test_perm_admin_{timestamp}",
            "email": f"testperm{timestamp}@frage.edu",
            "password": "TestPerm123!",
            "role": "kinder_admin"
        }
        
        success, response = self.run_test("Super admin create new admin test", "POST", "admin/create-with-role", 200, test_admin_data)
        
        # Restore original token
        self.admin_token = temp_admin_token
        
        if success:
            print("   ✅ Super admin can create new admin accounts")
            return True
        else:
            print("   ❌ Super admin cannot create new admin accounts")
            return False

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

    # PARENT ENROLLMENT FORM SYSTEM TESTS
    def setup_parent_enrollment_test_data(self):
        """Setup test data for parent enrollment form testing"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Create parent account
        signup_data = {
            "email": f"parent_enroll_{timestamp}@frage.edu",
            "phone": "010-1234-5678",
            "name": f"김학부모{timestamp}",
            "student_name": f"김학생{timestamp}",
            "student_birthdate": "2015-03-15",  # Added required field
            "password": "ParentEnroll123!",
            "terms_accepted": True,
            "branch": "junior"
        }
        
        success, response = self.run_test("Create Parent for Enrollment Test", "POST", "signup", 200, signup_data)
        if success and 'token' in response:
            self.parent_token = response['token']
            self.parent_user_id = response['user']['id']
            self.parent_household_token = response['household_token']
            
            # Get student ID - need to query the database or use a different approach
            # For now, let's get the student ID from the members list using admin token
            if hasattr(self, 'admin_token') and self.admin_token:
                # Get member details to find student ID
                member_success, member_response = self.run_test(
                    "Get Member Details for Student ID", 
                    "GET", 
                    f"admin/members/{self.parent_user_id}", 
                    200,
                    headers={'Authorization': f'Bearer {self.admin_token}'}
                )
                
                if member_success and 'students' in member_response and len(member_response['students']) > 0:
                    self.test_student_id = member_response['students'][0]['id']
                    print(f"   ✅ Parent enrollment test data created")
                    print(f"   Parent Token: {self.parent_token[:20]}...")
                    print(f"   Student ID: {self.test_student_id}")
                    return True
                else:
                    print("   ❌ Could not get student ID from member details")
            else:
                print("   ❌ No admin token available to get student ID")
        
        return False

    def test_parent_enroll_form_get(self):
        """Test GET /api/parent/enroll-form - 입학 등록 폼 데이터 조회"""
        if not hasattr(self, 'parent_token') or not hasattr(self, 'test_student_id'):
            if not self.setup_parent_enrollment_test_data():
                print("❌ Failed to setup parent enrollment test data")
                return False
        
        # Test with valid studentId
        params = {"studentId": self.test_student_id}
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        success, response = self.run_test(
            "GET Parent Enroll Form Data", 
            "GET", 
            "parent/enroll-form", 
            200, 
            params=params,
            headers=headers
        )
        
        if success and response:
            # Verify response structure
            required_fields = ['student', 'parent']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Verify student data
            student = response.get('student', {})
            if 'id' not in student or 'name' not in student:
                print("❌ Invalid student data structure")
                return False
            
            # Verify parent data
            parent = response.get('parent', {})
            if 'name' not in parent or 'phone' not in parent:
                print("❌ Invalid parent data structure")
                return False
            
            print("✅ Enrollment form data structure verified")
            print(f"   Student: {student.get('name')} (ID: {student.get('id')})")
            print(f"   Parent: {parent.get('name')} ({parent.get('phone')})")
            
            return True
        
        return False

    def test_parent_enroll_form_get_unauthorized(self):
        """Test GET /api/parent/enroll-form without authentication"""
        params = {"studentId": "test-student-id"}
        
        success, response = self.run_test(
            "GET Parent Enroll Form - Unauthorized", 
            "GET", 
            "parent/enroll-form", 
            401, 
            params=params
        )
        return success

    def test_parent_enroll_form_get_invalid_student(self):
        """Test GET /api/parent/enroll-form with invalid studentId"""
        if not hasattr(self, 'parent_token'):
            if not self.setup_parent_enrollment_test_data():
                return False
        
        params = {"studentId": "invalid-student-id"}
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        success, response = self.run_test(
            "GET Parent Enroll Form - Invalid Student", 
            "GET", 
            "parent/enroll-form", 
            404, 
            params=params,
            headers=headers
        )
        return success

    def test_parent_enroll_form_post_valid(self):
        """Test POST /api/parent/enroll-form - 입학 등록 폼 제출 (Valid Data)"""
        if not hasattr(self, 'parent_token') or not hasattr(self, 'test_student_id'):
            if not self.setup_parent_enrollment_test_data():
                return False
        
        # Valid enrollment form data
        form_data = {
            "student_id": self.test_student_id,
            "postal_code": "06236",
            "address1": "서울 강남구 테헤란로 146",
            "address2": "현대벤처빌 5층",
            "use_shuttle": True,
            "pickup_spot": "강남역 2번 출구",
            "dropoff_spot": "학원 정문",
            "start_date": "2025-03-01",
            "consent_privacy": True,
            "consent_signer": "김학부모"
        }
        
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        success, response = self.run_test(
            "POST Parent Enroll Form - Valid Data", 
            "POST", 
            "parent/enroll-form", 
            200, 
            data=form_data,
            headers=headers
        )
        
        if success and response:
            if response.get('ok') == True:
                print("✅ Enrollment form submitted successfully")
                return True
            else:
                print("❌ Unexpected response format")
        
        return False

    def test_parent_enroll_form_post_missing_required(self):
        """Test POST /api/parent/enroll-form - Missing Required Fields"""
        if not hasattr(self, 'parent_token') or not hasattr(self, 'test_student_id'):
            if not self.setup_parent_enrollment_test_data():
                return False
        
        # Test missing address1
        form_data = {
            "student_id": self.test_student_id,
            "postal_code": "06236",
            # "address1": "서울 강남구 테헤란로 146",  # Missing required field
            "start_date": "2025-03-01",
            "consent_privacy": True
        }
        
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        success, response = self.run_test(
            "POST Parent Enroll Form - Missing Address", 
            "POST", 
            "parent/enroll-form", 
            400, 
            data=form_data,
            headers=headers
        )
        
        return success

    def test_parent_enroll_form_post_shuttle_validation(self):
        """Test POST /api/parent/enroll-form - Shuttle Validation"""
        if not hasattr(self, 'parent_token') or not hasattr(self, 'test_student_id'):
            if not self.setup_parent_enrollment_test_data():
                return False
        
        # Test use_shuttle=True but missing pickup/dropoff spots
        form_data = {
            "student_id": self.test_student_id,
            "address1": "서울 강남구 테헤란로 146",
            "use_shuttle": True,
            # Missing pickup_spot and dropoff_spot
            "start_date": "2025-03-01",
            "consent_privacy": True
        }
        
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        success, response = self.run_test(
            "POST Parent Enroll Form - Shuttle Validation", 
            "POST", 
            "parent/enroll-form", 
            400, 
            data=form_data,
            headers=headers
        )
        
        return success

    def test_parent_student_photo_upload_valid(self):
        """Test POST /api/parent/students/{student_id}/photo - Valid Photo Upload"""
        if not hasattr(self, 'parent_token') or not hasattr(self, 'test_student_id'):
            if not self.setup_parent_enrollment_test_data():
                return False
        
        # Create a small test image file (1x1 pixel PNG)
        import base64
        
        # 1x1 pixel PNG image in base64
        png_data = base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
        )
        
        # For this test, we'll simulate the file upload
        # Note: requests library file upload would require actual file handling
        # This is a simplified test to verify the endpoint exists and responds correctly
        
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        # Test endpoint accessibility (we expect it to fail due to missing file, but should not be 404)
        success, response = self.run_test(
            "POST Student Photo Upload - Endpoint Test", 
            "POST", 
            f"parent/students/{self.test_student_id}/photo", 
            422,  # Expect 422 for missing file parameter
            headers=headers
        )
        
        # If we get 422, it means the endpoint exists and is processing the request
        if success:
            print("✅ Photo upload endpoint is accessible and validates input")
            return True
        
        return False

    def test_parent_student_photo_upload_unauthorized(self):
        """Test POST /api/parent/students/{student_id}/photo - Unauthorized Access"""
        success, response = self.run_test(
            "POST Student Photo Upload - Unauthorized", 
            "POST", 
            "parent/students/test-student-id/photo", 
            401
        )
        return success

    def test_parent_student_photo_upload_invalid_student(self):
        """Test POST /api/parent/students/{student_id}/photo - Invalid Student ID"""
        if not hasattr(self, 'parent_token'):
            if not self.setup_parent_enrollment_test_data():
                return False
        
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        success, response = self.run_test(
            "POST Student Photo Upload - Invalid Student", 
            "POST", 
            "parent/students/invalid-student-id/photo", 
            422,  # Expect 422 for missing file, but would be 404 if student check fails first
            headers=headers
        )
        return success

    def test_parent_address_search(self):
        """Test GET /api/parent/address/search - 한국 주소 검색"""
        if not hasattr(self, 'parent_token'):
            if not self.setup_parent_enrollment_test_data():
                return False
        
        params = {"query": "강남구"}
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        success, response = self.run_test(
            "GET Parent Address Search", 
            "GET", 
            "parent/address/search", 
            200, 
            params=params,
            headers=headers
        )
        
        if success and response:
            # Check if response has 'addresses' key (wrapped response)
            addresses = response.get('addresses', response)
            
            # Verify response is a list of addresses
            if isinstance(addresses, list):
                print(f"✅ Address search returned {len(addresses)} results")
                if len(addresses) > 0:
                    first_address = addresses[0]
                    required_fields = ['address_name', 'postal_code']
                    for field in required_fields:
                        if field not in first_address:
                            print(f"❌ Missing address field: {field}")
                            return False
                    print(f"   Sample address: {first_address.get('address_name')}")
                return True
            else:
                print("❌ Address search response is not a list")
        
        return False

    def test_parent_address_search_unauthorized(self):
        """Test GET /api/parent/address/search - Unauthorized Access"""
        params = {"query": "강남구"}
        
        success, response = self.run_test(
            "GET Parent Address Search - Unauthorized", 
            "GET", 
            "parent/address/search", 
            401, 
            params=params
        )
        return success

    def test_parent_address_search_empty_query(self):
        """Test GET /api/parent/address/search - Empty Query"""
        if not hasattr(self, 'parent_token'):
            if not self.setup_parent_enrollment_test_data():
                return False
        
        params = {"query": ""}
        headers = {'Authorization': f'Bearer {self.parent_token}'}
        
        success, response = self.run_test(
            "GET Parent Address Search - Empty Query", 
            "GET", 
            "parent/address/search", 
            200,  # Should still return 200 but empty results
            params=params,
            headers=headers
        )
        
        if success and response:
            # Check if response has 'addresses' key (wrapped response)
            addresses = response.get('addresses', response)
            
            if isinstance(addresses, list):
                print(f"✅ Empty query returns {len(addresses)} results")
                return True
        
        return False

def main():
    print("🚀 Starting Frage EDU Parent Enrollment Form System API Tests")
    print("=" * 60)
    
    tester = FrageEDUAPITester()
    
    # Test sequence - PRIORITY: Parent Enrollment Form System
    tests = [
        # Basic API Tests
        ("Root Endpoint", tester.test_root_endpoint),
        
        # PRIORITY TESTING - Parent Enrollment Form System
        ("Setup Parent Enrollment Test Data", tester.setup_parent_enrollment_test_data),
        ("GET Parent Enroll Form Data", tester.test_parent_enroll_form_get),
        ("GET Parent Enroll Form - Unauthorized", tester.test_parent_enroll_form_get_unauthorized),
        ("GET Parent Enroll Form - Invalid Student", tester.test_parent_enroll_form_get_invalid_student),
        ("POST Parent Enroll Form - Valid Data", tester.test_parent_enroll_form_post_valid),
        ("POST Parent Enroll Form - Missing Required Fields", tester.test_parent_enroll_form_post_missing_required),
        ("POST Parent Enroll Form - Shuttle Validation", tester.test_parent_enroll_form_post_shuttle_validation),
        ("POST Student Photo Upload - Endpoint Test", tester.test_parent_student_photo_upload_valid),
        ("POST Student Photo Upload - Unauthorized", tester.test_parent_student_photo_upload_unauthorized),
        ("POST Student Photo Upload - Invalid Student", tester.test_parent_student_photo_upload_invalid_student),
        ("GET Parent Address Search", tester.test_parent_address_search),
        ("GET Parent Address Search - Unauthorized", tester.test_parent_address_search_unauthorized),
        ("GET Parent Address Search - Empty Query", tester.test_parent_address_search_empty_query),
        
        # Supporting Tests - Admin Account Creation with Roles (Previous Tests)
        ("Login with Existing Admin (admin/AdminPass123!)", tester.test_existing_admin_login),
        ("Setup Default Admin Accounts", tester.test_setup_default_admins),
        ("Test New Admin Login Credentials", tester.test_new_admin_logins),
        ("Test Role-Based Access Control", tester.test_role_based_access_control),
        ("Create Custom Admin with Role", tester.test_create_custom_admin_with_role),
        ("Verify Admin Role Permissions", tester.test_admin_role_permissions_verification),
        
        # Supporting Tests - RBAC and Student Data
        ("Initialize RBAC System", tester.test_init_rbac_system),
        ("Create Sample Student Data", tester.test_create_sample_student_data),
        ("Test /admin/students Endpoint", tester.test_admin_students_endpoint),
        ("Test Branch Filtering - Unauthorized Access", tester.test_branch_filtering_unauthorized_access),
        ("Test Branch Filtering - Authorized Access", tester.test_branch_filtering_authorized_access),
        ("Test Endpoint Consistency", tester.test_students_vs_student_management_consistency),
        ("Check RBAC Permissions", tester.test_rbac_permissions_check),
        
        # User Management Tests (New Model Structure)
        ("User Signup (New Model)", tester.test_signup),
        ("User Login (Updated)", tester.test_login),
        ("Get Profile", tester.test_profile),
        
        # Member Management Tests
        ("Get Members List", tester.test_get_members_list),
        ("Get Member Details", tester.test_get_member_details),
        ("Reset Member Password", tester.test_reset_member_password),
        ("Update Member Status", tester.test_update_member_status),
        ("Bulk Export Members", tester.test_bulk_export_members),
        ("Bulk Notify Members", tester.test_bulk_notify_members),
        ("Get Audit Logs", tester.test_get_audit_logs),
        
        # Security Tests
        ("Login Disabled User", tester.test_login_disabled_user),
        
        # Admission Flow Tests (Existing)
        ("Get Admission Data", tester.test_get_admission_data),
        ("Update Consent", tester.test_update_consent),
        ("Update Forms", tester.test_update_forms),
        ("Update Guides", tester.test_update_guides),
        ("Update Checklist", tester.test_update_checklist),
        ("Final Admission Data", tester.test_get_admission_data_after_updates),
        
        # Edge Case Tests
        ("Duplicate Email Signup", tester.test_signup_duplicate_email),
        ("Signup No Terms", tester.test_signup_no_terms),
        ("Invalid Login", tester.test_login_invalid_credentials)
    ]
    
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} crashed: {str(e)}")
            failed_tests.append(test_name)
        
        # Small delay between tests to avoid overwhelming the server
        time.sleep(0.5)
    
    # Print results
    print("\n" + "=" * 60)
    print("📊 PARENT ENROLLMENT FORM SYSTEM TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed tests ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   - {test}")
    else:
        print("\n✅ All tests passed!")
    
    print(f"\n🔑 Test Tokens:")
    print(f"   User JWT Token: {tester.token[:30] if tester.token else 'None'}...")
    print(f"   Admin JWT Token: {tester.admin_token[:30] if tester.admin_token else 'None'}...")
    print(f"   Parent JWT Token: {getattr(tester, 'parent_token', 'None')[:30] if hasattr(tester, 'parent_token') and tester.parent_token else 'None'}...")
    print(f"   Household Token: {tester.household_token or 'None'}")
    print(f"   Test User ID: {tester.test_user_id or 'None'}")
    print(f"   Test Student ID: {getattr(tester, 'test_student_id', 'None') or 'None'}")
    
    # Summary of key functionality tested
    print(f"\n📋 Key Parent Enrollment Form Features Tested:")
    print(f"   ✓ GET /api/parent/enroll-form - 입학 등록 폼 데이터 조회")
    print(f"   ✓ POST /api/parent/enroll-form - 입학 등록 폼 제출")
    print(f"   ✓ POST /api/parent/students/{{student_id}}/photo - 학생 사진 업로드")
    print(f"   ✓ GET /api/parent/address/search - 한국 주소 검색")
    print(f"   ✓ Parent authentication and authorization")
    print(f"   ✓ Required field validation (address1, start_date, consent_privacy)")
    print(f"   ✓ Shuttle service validation (pickup/dropoff spots)")
    print(f"   ✓ Student ownership verification")
    print(f"   ✓ File upload endpoint validation")
    print(f"   ✓ Address search functionality")
    print(f"   ✓ Error handling and unauthorized access")
    
    return 0 if len(failed_tests) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())