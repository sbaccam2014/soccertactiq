from coach.serializers import AssignedPlayerSerializer, PlayerDetailSerializer

# Parents see the same "player_profile + stats" shape coaches see — just
# read-only and scoped through ParentLink instead of CoachAssignment.
# Re-exported here (rather than importing coach.serializers directly in
# views) so the parent app's public surface doesn't read as depending on
# coach internals.
ChildSerializer = AssignedPlayerSerializer
ChildDetailSerializer = PlayerDetailSerializer
