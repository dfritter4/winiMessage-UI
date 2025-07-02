export const mockThreads = [
  {
    thread_guid: "dm:+1234567890",
    thread_name: "John Doe",
    last_message: {
      text: "See you tomorrow!",
      timestamp: "2024-01-15T10:30:00Z",
      sender_name: "John Doe"
    },
    participants: ["You", "John Doe"],
    unread_count: 2,
    message_count: 156,
    thread_type: "direct",
    last_updated: "2024-01-15T10:30:00Z"
  },
  {
    thread_guid: "iMessage;+;chat123",
    thread_name: "Family Chat",
    last_message: {
      text: "Don't forget dinner at 7!",
      timestamp: "2024-01-15T09:15:00Z",
      sender_name: "Mom"
    },
    participants: ["You", "Mom", "Dad", "Sister"],
    unread_count: 0,
    message_count: 245,
    thread_type: "group",
    last_updated: "2024-01-15T09:15:00Z"
  },
  {
    thread_guid: "dm:+0987654321",
    thread_name: "Jane Smith",
    last_message: {
      text: "Thanks for the help with the project!",
      timestamp: "2024-01-14T16:45:00Z",
      sender_name: "Jane Smith"
    },
    participants: ["You", "Jane Smith"],
    unread_count: 1,
    message_count: 89,
    thread_type: "direct",
    last_updated: "2024-01-14T16:45:00Z"
  },
  {
    thread_guid: "iMessage;+;workteam",
    thread_name: "Work Team",
    last_message: {
      text: "Meeting moved to 3 PM",
      timestamp: "2024-01-14T14:20:00Z",
      sender_name: "Mike Johnson"
    },
    participants: ["You", "Mike Johnson", "Sarah Wilson", "Tom Brown"],
    unread_count: 3,
    message_count: 432,
    thread_type: "group",
    last_updated: "2024-01-14T14:20:00Z"
  },
  {
    thread_guid: "dm:+1122334455",
    thread_name: "Alex Rodriguez",
    last_message: {
      text: "Let's grab coffee this weekend",
      timestamp: "2024-01-13T19:30:00Z",
      sender_name: "Alex Rodriguez"
    },
    participants: ["You", "Alex Rodriguez"],
    unread_count: 0,
    message_count: 67,
    thread_type: "direct",
    last_updated: "2024-01-13T19:30:00Z"
  }
];

export const mockMessages = {
  "dm:+1234567890": [
    {
      guid: "msg-1",
      text: "Hey, how's it going?",
      timestamp: "2024-01-15T08:00:00Z",
      sender_name: "John Doe",
      thread_name: "John Doe",
      thread_guid: "dm:+1234567890",
      direction: "incoming",
      service: "iMessage",
      reactions: [
        { type: "thumbs_up", count: 1, reactors: ["You"] }
      ]
    },
    {
      guid: "msg-2",
      text: "Pretty good! Just working on some projects.",
      timestamp: "2024-01-15T08:05:00Z",
      sender_name: "You",
      thread_name: "John Doe",
      thread_guid: "dm:+1234567890",
      direction: "outgoing",
      service: "iMessage"
    },
    {
      guid: "msg-3",
      text: "That's awesome. Are we still on for tomorrow?",
      timestamp: "2024-01-15T08:10:00Z",
      sender_name: "John Doe",
      thread_name: "John Doe",
      thread_guid: "dm:+1234567890",
      direction: "incoming",
      service: "iMessage",
      reactions: [
        { type: "haha", count: 2, reactors: ["You", "Someone"] },
        { type: "heart", count: 1, reactors: ["You"] }
      ]
    },
    {
      guid: "msg-4",
      text: "Absolutely! What time works for you?",
      timestamp: "2024-01-15T08:15:00Z",
      sender_name: "You",
      thread_name: "John Doe",
      thread_guid: "dm:+1234567890",
      direction: "outgoing",
      service: "iMessage"
    },
    {
      guid: "msg-5",
      text: "Check out this video! https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      timestamp: "2024-01-15T10:25:00Z",
      sender_name: "John Doe",
      thread_name: "John Doe",
      thread_guid: "dm:+1234567890",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-6",
      text: "See you tomorrow!",
      timestamp: "2024-01-15T10:30:00Z",
      sender_name: "John Doe",
      thread_name: "John Doe",
      thread_guid: "dm:+1234567890",
      direction: "incoming",
      service: "iMessage"
    }
  ],
  "iMessage;+;chat123": [
    {
      guid: "msg-family-1",
      text: "Good morning everyone!",
      timestamp: "2024-01-15T07:00:00Z",
      sender_name: "Mom",
      thread_name: "Family Chat",
      thread_guid: "iMessage;+;chat123",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-family-2",
      text: "Morning mom!",
      timestamp: "2024-01-15T07:05:00Z",
      sender_name: "You",
      thread_name: "Family Chat",
      thread_guid: "iMessage;+;chat123",
      direction: "outgoing",
      service: "iMessage"
    },
    {
      guid: "msg-family-3",
      text: "Hey everyone",
      timestamp: "2024-01-15T07:10:00Z",
      sender_name: "Sister",
      thread_name: "Family Chat",
      thread_guid: "iMessage;+;chat123",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-family-4",
      text: "Don't forget dinner at 7!",
      timestamp: "2024-01-15T09:15:00Z",
      sender_name: "Mom",
      thread_name: "Family Chat",
      thread_guid: "iMessage;+;chat123",
      direction: "incoming",
      service: "iMessage",
      reactions: [
        { type: "thumbs_up", count: 3, reactors: ["You", "Dad", "Sister"] },
        { type: "exclamation", count: 1, reactors: ["Dad"] }
      ]
    }
  ],
  "dm:+0987654321": [
    {
      guid: "msg-jane-1",
      text: "Hey, could you help me with the React component?",
      timestamp: "2024-01-14T15:30:00Z",
      sender_name: "Jane Smith",
      thread_name: "Jane Smith",
      thread_guid: "dm:+0987654321",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-jane-2",
      text: "Sure! What specifically are you having trouble with?",
      timestamp: "2024-01-14T15:35:00Z",
      sender_name: "You",
      thread_name: "Jane Smith",
      thread_guid: "dm:+0987654321",
      direction: "outgoing",
      service: "iMessage"
    },
    {
      guid: "msg-jane-3",
      text: "The state management part is confusing me",
      timestamp: "2024-01-14T15:40:00Z",
      sender_name: "Jane Smith",
      thread_name: "Jane Smith",
      thread_guid: "dm:+0987654321",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-jane-4",
      text: "Thanks for the help with the project!",
      timestamp: "2024-01-14T16:45:00Z",
      sender_name: "Jane Smith",
      thread_name: "Jane Smith",
      thread_guid: "dm:+0987654321",
      direction: "incoming",
      service: "iMessage"
    }
  ],
  "iMessage;+;workteam": [
    {
      guid: "msg-work-1",
      text: "Good morning team!",
      timestamp: "2024-01-14T09:00:00Z",
      sender_name: "Mike Johnson",
      thread_name: "Work Team",
      thread_guid: "iMessage;+;workteam",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-work-2",
      text: "Morning Mike!",
      timestamp: "2024-01-14T09:05:00Z",
      sender_name: "You",
      thread_name: "Work Team",
      thread_guid: "iMessage;+;workteam",
      direction: "outgoing",
      service: "iMessage"
    },
    {
      guid: "msg-work-3",
      text: "Ready for the big presentation today?",
      timestamp: "2024-01-14T09:10:00Z",
      sender_name: "Sarah Wilson",
      thread_name: "Work Team",
      thread_guid: "iMessage;+;workteam",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-work-4",
      text: "Meeting moved to 3 PM",
      timestamp: "2024-01-14T14:20:00Z",
      sender_name: "Mike Johnson",
      thread_name: "Work Team",
      thread_guid: "iMessage;+;workteam",
      direction: "incoming",
      service: "iMessage"
    }
  ],
  "dm:+1122334455": [
    {
      guid: "msg-alex-1",
      text: "How was your weekend?",
      timestamp: "2024-01-13T18:00:00Z",
      sender_name: "Alex Rodriguez",
      thread_name: "Alex Rodriguez",
      thread_guid: "dm:+1122334455",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-alex-2",
      text: "It was great! Went hiking with some friends.",
      timestamp: "2024-01-13T18:15:00Z",
      sender_name: "You",
      thread_name: "Alex Rodriguez",
      thread_guid: "dm:+1122334455",
      direction: "outgoing",
      service: "iMessage"
    },
    {
      guid: "msg-alex-3",
      text: "That sounds awesome! I love hiking.",
      timestamp: "2024-01-13T18:30:00Z",
      sender_name: "Alex Rodriguez",
      thread_name: "Alex Rodriguez",
      thread_guid: "dm:+1122334455",
      direction: "incoming",
      service: "iMessage"
    },
    {
      guid: "msg-alex-4",
      text: "Let's grab coffee this weekend",
      timestamp: "2024-01-13T19:30:00Z",
      sender_name: "Alex Rodriguez",
      thread_name: "Alex Rodriguez",
      thread_guid: "dm:+1122334455",
      direction: "incoming",
      service: "iMessage"
    }
  ]
};