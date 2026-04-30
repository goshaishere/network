P0_PERMISSION_MAP: dict[str, dict[str, str]] = {
    "WorkDashboardView": {"GET": "work.dashboard.read"},
    "TasksGroupsView": {"GET": "work.group.read", "POST": "work.group.write"},
    "TasksBoardsView": {"GET": "work.board.read", "POST": "work.board.write"},
    "TasksColumnsView": {"GET": "work.column.read", "POST": "work.column.write"},
    "TasksListCreateView": {"GET": "work.task.read", "POST": "work.task.write"},
    "TasksColumnsReorderView": {"POST": "work.column.write"},
    "TasksDetailView": {"PATCH": "work.task.write"},
    "InternalStatusView": {"GET": "internal.tools"},
    "InternalWorkDashboardView": {"GET": "work.advanced"},
    "PrometheusMetricsView": {"GET": "internal.metrics.read"},
}

P1_PERMISSION_MAP: dict[str, dict[str, str]] = {
    "ConversationListCreateView": {"GET": "messaging.read", "POST": "messaging.write"},
    "MessageListCreateView": {"GET": "messaging.read", "POST": "messaging.write"},
    "FeedView": {"GET": "social.read"},
    "FriendsListView": {"GET": "social.read"},
    "FriendRequestCreateView": {"POST": "social.write"},
    "FriendRequestIncomingView": {"GET": "social.read"},
    "FriendRequestAcceptView": {"POST": "social.write"},
    "FriendRequestRejectView": {"POST": "social.write"},
    "ContentReportCreateView": {"POST": "moderation.report.write"},
    "MediaUploadView": {"POST": "media.upload"},
    "ProfileMeView": {"GET": "profiles.self.read", "PATCH": "profiles.self.write"},
    "DashboardLayoutView": {"GET": "profiles.self.read", "PATCH": "profiles.self.write"},
    "ProfileDetailView": {"GET": "profiles.read"},
}
