"""
Test script for role-based authentication system
"""

import asyncio
import httpx
from utils.security import decode_access_token

BASE_URL = "http://localhost:8000"

async def test_authentication_flow():
    """Test the complete authentication flow"""
    
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("TESTING ROLE-BASED AUTHENTICATION SYSTEM")
        print("=" * 60)
        
        # Test 1: Teacher Login
        print("\n1. Testing Teacher Login...")
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": "teacher@example.com",
                    "password": "password123",
                    "role": "teacher"
                }
            )
            if response.status_code == 200:
                data = response.json()
                token = data["token"]
                print("   ✓ Login successful")
                print(f"   Token received: {token[:50]}...")
                
                # Decode token to verify role
                payload = decode_access_token(token)
                print(f"   Token contains:")
                print(f"     - User ID: {payload['sub']}")
                print(f"     - Role: {payload['role']}")
                print(f"     - Expires: {payload['exp']}")
                
                # Test accessing teacher endpoint
                print("\n2. Testing Teacher Endpoint Access...")
                response = await client.get(
                    f"{BASE_URL}/teacher/assignments",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    print("   ✓ Successfully accessed teacher endpoint")
                else:
                    print(f"   ✗ Failed: {response.status_code} - {response.text}")
                
                # Test accessing admin endpoint (should fail)
                print("\n3. Testing Admin Endpoint Access (should be denied)...")
                response = await client.get(
                    f"{BASE_URL}/admin/students",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 403:
                    print("   ✓ Correctly denied access (403 Forbidden)")
                else:
                    print(f"   ✗ Unexpected response: {response.status_code}")
                
            else:
                print(f"   ✗ Login failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        # Test 2: Student Login
        print("\n4. Testing Student Login...")
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": "student@example.com",
                    "password": "password123",
                    "role": "student"
                }
            )
            if response.status_code == 200:
                data = response.json()
                token = data["token"]
                print("   ✓ Login successful")
                
                payload = decode_access_token(token)
                print(f"   Token role: {payload['role']}")
                
                # Test accessing student endpoint
                print("\n5. Testing Student Endpoint Access...")
                response = await client.get(
                    f"{BASE_URL}/student/assignments",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    print("   ✓ Successfully accessed student endpoint")
                else:
                    print(f"   Status: {response.status_code}")
                
            else:
                print(f"   ✗ Login failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        # Test 3: Admin Login
        print("\n6. Testing Admin Login...")
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": "admin@example.com",
                    "password": "admin123",
                    "role": "admin"
                }
            )
            if response.status_code == 200:
                data = response.json()
                token = data["token"]
                print("   ✓ Login successful")
                
                payload = decode_access_token(token)
                print(f"   Token role: {payload['role']}")
                
                # Test accessing admin endpoint
                print("\n7. Testing Admin Endpoint Access...")
                response = await client.get(
                    f"{BASE_URL}/admin/students",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    print("   ✓ Successfully accessed admin endpoint")
                else:
                    print(f"   Status: {response.status_code}")
                
            else:
                print(f"   ✗ Login failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        # Test 4: No Token
        print("\n8. Testing Endpoint Without Token (should be denied)...")
        try:
            response = await client.get(f"{BASE_URL}/teacher/assignments")
            if response.status_code == 401:
                print("   ✓ Correctly denied access (401 Unauthorized)")
            else:
                print(f"   ✗ Unexpected response: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        # Test 5: Invalid Token
        print("\n9. Testing Endpoint With Invalid Token (should be denied)...")
        try:
            response = await client.get(
                f"{BASE_URL}/teacher/assignments",
                headers={"Authorization": "Bearer invalid_token_here"}
            )
            if response.status_code == 401:
                print("   ✓ Correctly denied access (401 Unauthorized)")
            else:
                print(f"   ✗ Unexpected response: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        # Test 6: /me endpoint
        print("\n10. Testing /me Endpoint...")
        try:
            # Login first
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={
                    "email": "teacher@example.com",
                    "password": "password123",
                    "role": "teacher"
                }
            )
            if response.status_code == 200:
                token = response.json()["token"]
                
                # Get user info
                response = await client.get(
                    f"{BASE_URL}/auth/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    user_data = response.json()
                    print("   ✓ Successfully retrieved user info")
                    print(f"     - Name: {user_data.get('name')}")
                    print(f"     - Email: {user_data.get('email')}")
                    print(f"     - Role: {user_data.get('role')}")
                else:
                    print(f"   ✗ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    print("\nMake sure the backend server is running on http://localhost:8000\n")
    asyncio.run(test_authentication_flow())
