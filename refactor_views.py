import re

with open('/home/ismoilow/Desktop/easy_build/build/views.py', 'r') as f:
    content = f.read()

# Replace toggle_post_like
content = re.sub(
    r"@api_view\(\['POST'\]\)\s*@permission_classes\(\[IsAuthenticated\]\)\s*def toggle_post_like\(request, post_id\):",
    r"class TogglePostLikeAPIView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def post(self, request, post_id):",
    content
)

# Replace toggle_post_bookmark
content = re.sub(
    r"@api_view\(\['POST'\]\)\s*@permission_classes\(\[IsAuthenticated\]\)\s*def toggle_post_bookmark\(request, post_id\):",
    r"class TogglePostBookmarkAPIView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def post(self, request, post_id):",
    content
)

# Replace get_user_contact_info
content = re.sub(
    r"@api_view\(\['GET'\]\)\s*@permission_classes\(\[IsAuthenticated\]\)\s*def get_user_contact_info\(request, user_id\):",
    r"class UserContactInfoAPIView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def get(self, request, user_id):",
    content
)

# Replace search_users
content = re.sub(
    r"@api_view\(\['GET'\]\)\s*@permission_classes\(\[IsAuthenticated\]\)\s*def search_users\(request\):",
    r"class SearchUsersAPIView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def get(self, request):",
    content
)

# Replace add_team_member
content = re.sub(
    r"@api_view\(\['POST'\]\)\s*@permission_classes\(\[IsAuthenticated\]\)\s*def add_team_member\(request, user_id\):",
    r"class AddTeamMemberAPIView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def post(self, request, user_id):",
    content
)

# Replace remove_team_member
content = re.sub(
    r"@api_view\(\['POST'\]\)\s*@permission_classes\(\[IsAuthenticated\]\)\s*def remove_team_member\(request, user_id\):",
    r"class RemoveTeamMemberAPIView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def post(self, request, user_id):",
    content
)

# Replace respond_team_invite
content = re.sub(
    r"@api_view\(\['POST'\]\)\s*@permission_classes\(\[IsAuthenticated\]\)\s*def respond_team_invite\(request, invite_id\):",
    r"class RespondTeamInviteAPIView(APIView):\n    permission_classes = [IsAuthenticated]\n\n    def post(self, request, invite_id):",
    content
)

with open('/home/ismoilow/Desktop/easy_build/build/views.py', 'w') as f:
    f.write(content)

print("Done")
