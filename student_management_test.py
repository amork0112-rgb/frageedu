#!/usr/bin/env python3
"""
Student Management Interface Testing Script
Focus: Testing the new Student Management interface with sample data

TESTING PRIORITIES (as per review request):
1. Create sample student data using the /admin/create-sample-data endpoint
2. Test the /admin/students endpoint to verify data is returned correctly
3. Initialize RBAC system to ensure permissions are set up
4. Test different admin role access to verify RBAC filtering works

AUTHENTICATION: Use super_admin credentials: super_admin/Super123!
"""

import requests
import json
import sys
from datetime import datetime

class StudentManagementTester:
    def __init__(self, base_url="https://edu-admin-portal-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.super_admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        
    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {name}")
            if details:
                print(f"   {details}")
        print()

    def make_request(self, method, endpoint, data=None, params=None, token=None):
        """Make API request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=10)
            
            return response.status_code, response.json() if response.content else {}
        except Exception as e:
            return 500, {"error": str(e)}

    def test_super_admin_login(self):
        """Test login with super_admin credentials"""
        print("🔐 Testing Super Admin Authentication...")
        
        login_data = {
            "username": "super_admin",
            "password": "Super123!"
        }
        
        status, response = self.make_request('POST', 'admin/login', login_data)
        
        if status == 200 and 'token' in response:
            self.super_admin_token = response['token']
            admin_info = response.get('admin', {})
            role = admin_info.get('role', 'unknown')
            username = admin_info.get('username', 'unknown')
            
            self.log_test(
                "Super Admin Login", 
                True, 
                f"Successfully logged in as {username} with role: {role}"
            )
            return True
        else:
            self.log_test(
                "Super Admin Login", 
                False, 
                f"Login failed - Status: {status}, Response: {response}"
            )
            return False

    def test_create_sample_data(self):
        """Test creating sample student data"""
        print("📊 Testing Sample Student Data Creation...")
        
        if not self.super_admin_token:
            self.log_test("Create Sample Data", False, "No admin token available")
            return False
        
        status, response = self.make_request('POST', 'admin/create-sample-data', token=self.super_admin_token)
        
        if status == 200:
            message = response.get('message', '')
            created_parents = response.get('created_parents', 0)
            created_students = response.get('created_students', 0)
            
            if 'already exist' in message:
                self.log_test(
                    "Create Sample Data", 
                    True, 
                    f"Sample data already exists: {message}"
                )
            else:
                self.log_test(
                    "Create Sample Data", 
                    True, 
                    f"Created {created_parents} parents and {created_students} students"
                )
            return True
        else:
            self.log_test(
                "Create Sample Data", 
                False, 
                f"Failed - Status: {status}, Response: {response}"
            )
            return False

    def test_rbac_initialization(self):
        """Test RBAC system initialization"""
        print("🔒 Testing RBAC System Initialization...")
        
        if not self.super_admin_token:
            self.log_test("RBAC Initialization", False, "No admin token available")
            return False
        
        status, response = self.make_request('POST', 'admin/init-rbac', token=self.super_admin_token)
        
        if status == 200:
            message = response.get('message', 'RBAC initialized')
            self.log_test(
                "RBAC Initialization", 
                True, 
                f"RBAC system ready: {message}"
            )
            return True
        else:
            self.log_test(
                "RBAC Initialization", 
                False, 
                f"Failed - Status: {status}, Response: {response}"
            )
            return False

    def test_admin_students_endpoint(self):
        """Test /admin/students endpoint with super_admin"""
        print("👥 Testing /admin/students Endpoint...")
        
        if not self.super_admin_token:
            self.log_test("Admin Students Endpoint", False, "No admin token available")
            return False
        
        status, response = self.make_request('GET', 'admin/students', token=self.super_admin_token)
        
        if status == 200:
            students = response.get('students', [])
            allowed_branches = response.get('allowed_branches', [])
            permissions = response.get('user_permissions', [])
            pagination = response.get('pagination', {})
            
            details = f"""
   Students found: {len(students)}
   Allowed branches: {allowed_branches}
   Permissions: {len(permissions)} ({', '.join(permissions[:3])}...)
   Total in DB: {pagination.get('total', 0)}"""
            
            self.log_test("Admin Students Endpoint", True, details)
            
            # Show sample student data
            if students:
                print("📋 Sample Student Data:")
                for i, student in enumerate(students[:3]):  # Show first 3
                    print(f"   {i+1}. {student.get('name', 'N/A')} - Branch: {student.get('branch', 'N/A')} - Grade: {student.get('grade', 'N/A')}")
                if len(students) > 3:
                    print(f"   ... and {len(students) - 3} more students")
                print()
            
            return True
        else:
            self.log_test(
                "Admin Students Endpoint", 
                False, 
                f"Failed - Status: {status}, Response: {response}"
            )
            return False

    def test_role_based_access(self):
        """Test different admin role access to verify RBAC filtering"""
        print("🎭 Testing Role-Based Access Control...")
        
        admin_roles = [
            {"username": "super_admin", "password": "Super123!", "expected_branches": ["kinder", "junior", "middle", "kinder_single"]},
            {"username": "kinder_admin", "password": "Kinder123!", "expected_branches": ["kinder"]},
            {"username": "junior_admin", "password": "Junior123!", "expected_branches": ["junior", "kinder_single", "middle"]},
            {"username": "middle_admin", "password": "Middle123!", "expected_branches": ["middle"]}
        ]
        
        rbac_results = []
        
        for admin in admin_roles:
            print(f"   Testing {admin['username']}...")
            
            # Login as this admin
            login_data = {
                "username": admin["username"],
                "password": admin["password"]
            }
            
            status, login_response = self.make_request('POST', 'admin/login', login_data)
            if status != 200:
                print(f"   ❌ Login failed for {admin['username']}")
                rbac_results.append(False)
                continue
            
            admin_token = login_response['token']
            
            # Test access to students endpoint
            status, response = self.make_request('GET', 'admin/students', token=admin_token)
            if status != 200:
                print(f"   ❌ Students endpoint failed for {admin['username']}")
                rbac_results.append(False)
                continue
            
            allowed_branches = response.get('allowed_branches', [])
            students = response.get('students', [])
            expected_branches = admin['expected_branches']
            
            # Check branch access
            branches_match = set(allowed_branches) == set(expected_branches)
            if branches_match:
                print(f"   ✅ {admin['username']}: Correct branch access {allowed_branches}")
            else:
                print(f"   ❌ {admin['username']}: Branch mismatch - expected {expected_branches}, got {allowed_branches}")
            
            # Verify students are from allowed branches only
            unauthorized_students = [s for s in students if s.get('branch') not in allowed_branches]
            if not unauthorized_students:
                print(f"   ✅ {admin['username']}: All {len(students)} students from authorized branches")
                rbac_results.append(branches_match)
            else:
                print(f"   ❌ {admin['username']}: Found {len(unauthorized_students)} students from unauthorized branches")
                rbac_results.append(False)
        
        success_count = sum(rbac_results)
        self.log_test(
            "Role-Based Access Control", 
            success_count == len(admin_roles), 
            f"Successful RBAC tests: {success_count}/{len(admin_roles)}"
        )
        
        return success_count == len(admin_roles)

    def test_branch_filtering(self):
        """Test branch filtering functionality"""
        print("🌿 Testing Branch Filtering...")
        
        if not self.super_admin_token:
            self.log_test("Branch Filtering", False, "No admin token available")
            return False
        
        # Test filtering by each branch
        branches_to_test = ["kinder", "junior", "middle"]
        filtering_results = []
        
        for branch in branches_to_test:
            params = {"branch_filter": branch}
            status, response = self.make_request('GET', 'admin/students', params=params, token=self.super_admin_token)
            
            if status == 200:
                students = response.get('students', [])
                # Verify all returned students are from the requested branch
                correct_branch_students = [s for s in students if s.get('branch') == branch]
                
                if len(correct_branch_students) == len(students):
                    print(f"   ✅ {branch} filter: {len(students)} students correctly filtered")
                    filtering_results.append(True)
                else:
                    print(f"   ❌ {branch} filter: Found students from other branches")
                    filtering_results.append(False)
            else:
                print(f"   ❌ {branch} filter: Request failed")
                filtering_results.append(False)
        
        success_count = sum(filtering_results)
        self.log_test(
            "Branch Filtering", 
            success_count == len(branches_to_test), 
            f"Successful branch filters: {success_count}/{len(branches_to_test)}"
        )
        
        return success_count == len(branches_to_test)

    def test_student_management_interface(self):
        """Test the complete Student Management interface"""
        print("🎯 Testing Complete Student Management Interface...")
        
        if not self.super_admin_token:
            self.log_test("Student Management Interface", False, "No admin token available")
            return False
        
        # Test both endpoints for consistency
        endpoints = [
            ("admin/students", "Students Endpoint"),
            ("admin/student-management", "Student Management Endpoint")
        ]
        
        endpoint_results = []
        responses = []
        
        for endpoint, name in endpoints:
            status, response = self.make_request('GET', endpoint, token=self.super_admin_token)
            
            if status == 200:
                students = response.get('students', [])
                branches = response.get('allowed_branches', [])
                permissions = response.get('user_permissions', [])
                
                print(f"   ✅ {name}: {len(students)} students, {len(branches)} branches, {len(permissions)} permissions")
                endpoint_results.append(True)
                responses.append(response)
            else:
                print(f"   ❌ {name}: Failed with status {status}")
                endpoint_results.append(False)
                responses.append({})
        
        # Check consistency between endpoints
        if len(responses) == 2 and all(endpoint_results):
            students1 = len(responses[0].get('students', []))
            students2 = len(responses[1].get('students', []))
            branches1 = responses[0].get('allowed_branches', [])
            branches2 = responses[1].get('allowed_branches', [])
            
            consistent = students1 == students2 and branches1 == branches2
            if consistent:
                print(f"   ✅ Endpoint Consistency: Both endpoints return identical data")
            else:
                print(f"   ❌ Endpoint Consistency: Endpoints return different data")
            endpoint_results.append(consistent)
        
        success_count = sum(endpoint_results)
        total_tests = len(endpoint_results)
        
        self.log_test(
            "Student Management Interface", 
            success_count == total_tests, 
            f"Interface tests passed: {success_count}/{total_tests}"
        )
        
        return success_count == total_tests

    def run_all_tests(self):
        """Run all Student Management interface tests"""
        print("🚀 Starting Student Management Interface Testing")
        print("=" * 60)
        print("FOCUS: Testing Student Management interface with sample data")
        print("AUTH: Using super_admin credentials (super_admin/Super123!)")
        print("=" * 60)
        print()
        
        # Test sequence as per review request
        tests = [
            ("Super Admin Authentication", self.test_super_admin_login),
            ("Create Sample Student Data", self.test_create_sample_data),
            ("Initialize RBAC System", self.test_rbac_initialization),
            ("Test /admin/students Endpoint", self.test_admin_students_endpoint),
            ("Test Role-Based Access Control", self.test_role_based_access),
            ("Test Branch Filtering", self.test_branch_filtering),
            ("Test Student Management Interface", self.test_student_management_interface)
        ]
        
        failed_tests = []
        
        for test_name, test_func in tests:
            print(f"{'='*20} {test_name} {'='*20}")
            try:
                success = test_func()
                if not success:
                    failed_tests.append(test_name)
            except Exception as e:
                print(f"❌ {test_name} crashed: {str(e)}")
                failed_tests.append(test_name)
                self.tests_run += 1
        
        # Print final results
        print("=" * 60)
        print("📊 STUDENT MANAGEMENT INTERFACE TEST RESULTS")
        print("=" * 60)
        print(f"Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if failed_tests:
            print(f"\n❌ Failed tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   - {test}")
        else:
            print("\n✅ All Student Management interface tests passed!")
        
        print(f"\n🔑 Authentication Token:")
        print(f"   Super Admin Token: {self.super_admin_token[:30] if self.super_admin_token else 'None'}...")
        
        print(f"\n📋 Key Features Tested:")
        print(f"   ✓ Super admin authentication (super_admin/Super123!)")
        print(f"   ✓ Sample student data creation/verification")
        print(f"   ✓ RBAC system initialization")
        print(f"   ✓ /admin/students endpoint functionality")
        print(f"   ✓ Role-based access control for different admin types")
        print(f"   ✓ Branch filtering functionality")
        print(f"   ✓ Student Management interface consistency")
        
        return len(failed_tests) == 0

def main():
    tester = StudentManagementTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())