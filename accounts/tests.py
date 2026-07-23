from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from build.models import Plan, BuilderProfile, SubscriptionRequest
from chat.models import ChatRoom, Message


class SubscriptionSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create Plans
        self.basic_plan = Plan.objects.create(
            name='Basic', price=10.00, description='Basic Package', duration_days=30
        )
        # Create Admin
        self.admin_user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='adminpassword'
        )
        # Create Builder
        self.builder_user = User.objects.create_user(
            username='builder1', email='builder@test.com', password='builderpassword'
        )
        self.builder_profile = self.builder_user.profile
        self.builder_profile.role = 'builder'
        self.builder_profile.save()
        
        self.bp, _ = BuilderProfile.objects.get_or_create(
            profile=self.builder_profile,
            defaults={'profession': 'Usta'}
        )

    def test_plan_selection(self):
        self.client.login(username='builder1', password='builderpassword')
        response = self.client.get(f'/uz/plans/{self.basic_plan.id}/subscribe/')
        
        self.bp.refresh_from_db()
        self.assertEqual(self.bp.pending_plan, self.basic_plan)
        
        # Should redirect to chatroom with admin
        room = ChatRoom.objects.filter(participants=self.builder_user).filter(participants=self.admin_user).first()
        self.assertIsNotNone(room)
        self.assertRedirects(response, f'/uz/chat/?room_id={room.id}', fetch_redirect_response=False)

    def test_payment_screenshot_upload_grants_temp_access(self):
        self.client.login(username='builder1', password='builderpassword')
        # Select plan first
        self.bp.pending_plan = self.basic_plan
        self.bp.save()
        
        # Get/create chatroom
        room, _ = ChatRoom.get_or_create_for(self.builder_user, self.admin_user)
        
        # Simulate file upload via api_upload_file
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile("screenshot.png", b"file_content", content_type="image/png")
        
        response = self.client.post(
            f'/uz/chat/api/upload/{room.id}/',
            {'file': test_image, 'file_type': 'image', 'content': 'Chek yubordim'},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify SubscriptionRequest is created
        sub_req = SubscriptionRequest.objects.filter(user=self.builder_user).first()
        self.assertIsNotNone(sub_req)
        self.assertEqual(sub_req.plan_name, self.basic_plan.name)
        self.assertEqual(sub_req.status, 'pending')
        
        # Verify temporary access is granted
        self.bp.refresh_from_db()
        self.assertTrue(self.bp.is_temp_active)
        self.assertTrue(self.bp.temp_active_until > timezone.now())
        self.assertTrue(self.bp.has_active_subscription)
        
        # Verify system confirmation message exists
        sys_msg = Message.objects.filter(room=room, sender=self.admin_user).last()
        self.assertIsNotNone(sys_msg)
        self.assertIn("vaqtinchalik kirish imkoni berildi", sys_msg.content)

    def test_admin_accept_verification(self):
        # Create a pending request
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile("screenshot.png", b"file_content", content_type="image/png")
        
        sub_req = SubscriptionRequest.objects.create(
            user=self.builder_user,
            plan_name=self.basic_plan.name,
            amount=self.basic_plan.price,
            screenshot=test_image,
            status='pending'
        )
        
        self.bp.pending_plan = self.basic_plan
        self.bp.is_temp_active = True
        self.bp.temp_active_until = timezone.now() + timezone.timedelta(hours=24)
        self.bp.save()
        
        # Login as Admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(f'/uz/verification/{sub_req.id}/accept/')
        
        # Verify request is accepted
        sub_req.refresh_from_db()
        self.assertEqual(sub_req.status, 'accepted')
        
        # Verify builder profile subscription state
        self.bp.refresh_from_db()
        self.assertTrue(self.bp.subscription_status)
        self.assertEqual(self.bp.subscription_plan, self.basic_plan)
        self.assertFalse(self.bp.is_temp_active)
        self.assertIsNone(self.bp.pending_plan)
        
        # Verify system message in chat
        room = ChatRoom.objects.filter(participants=self.builder_user).filter(participants=self.admin_user).first()
        msg = Message.objects.filter(room=room, sender=self.admin_user).last()
        self.assertIsNotNone(msg)
        self.assertIn("doimiy faollashtirildi", msg.content)

    def test_admin_reject_verification(self):
        # Create a pending request
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile("screenshot.png", b"file_content", content_type="image/png")
        
        sub_req = SubscriptionRequest.objects.create(
            user=self.builder_user,
            plan_name=self.basic_plan.name,
            amount=self.basic_plan.price,
            screenshot=test_image,
            status='pending'
        )
        
        self.bp.pending_plan = self.basic_plan
        self.bp.is_temp_active = True
        self.bp.temp_active_until = timezone.now() + timezone.timedelta(hours=24)
        self.bp.save()
        
        # Login as Admin
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(f'/uz/verification/{sub_req.id}/reject/')
        
        # Verify request is rejected
        sub_req.refresh_from_db()
        self.assertEqual(sub_req.status, 'rejected')
        
        # Verify builder profile subscription state
        self.bp.refresh_from_db()
        self.assertFalse(self.bp.subscription_status)
        self.assertIsNone(self.bp.subscription_plan)
        self.assertFalse(self.bp.is_temp_active)
        
        # Verify automatic warning notification message from Admin in chat
        room = ChatRoom.objects.filter(participants=self.builder_user).filter(participants=self.admin_user).first()
        msg = Message.objects.filter(room=room, sender=self.admin_user).last()
        self.assertIsNotNone(msg)
        self.assertIn("To'lov tasdiqlanmadi", msg.content)

    def test_payment_dashboard_view(self):
        self.client.login(username='builder1', password='builderpassword')
        
        # Get/create chatroom
        room, _ = ChatRoom.get_or_create_for(self.builder_user, self.admin_user)
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_image = SimpleUploadedFile("screenshot.png", b"file_content", content_type="image/png")
        
        response = self.client.post(
            '/uz/payment-dashboard/',
            {'plan_name': 'Premium', 'amount': '29.00', 'screenshot': test_image},
            format='multipart'
        )
        
        # Redirects to dashboard
        self.assertRedirects(response, '/uz/payment-dashboard/')
        
        # Verify SubscriptionRequest exists
        sub_req = SubscriptionRequest.objects.filter(user=self.builder_user).last()
        self.assertIsNotNone(sub_req)
        self.assertEqual(sub_req.plan_name, 'Premium')
        self.assertEqual(sub_req.amount, 29.00)
        self.assertEqual(sub_req.status, 'pending')
        
        # Verify temporary access granted
        self.bp.refresh_from_db()
        self.assertTrue(self.bp.is_temp_active)
        
        # Verify automated chat message: "To'lov cheki yuborildi"
        msg = Message.objects.filter(room=room, sender=self.builder_user).last()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.content, "To'lov cheki yuborildi")

    def test_superadmin_dashboard_view(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get('/uz/superadmin/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_users_count', response.context)
