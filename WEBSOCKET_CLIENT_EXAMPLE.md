# WebSocket Client Example

Hướng dẫn kết nối và xử lý WebSocket để nhận real-time updates từ server.

## 1. Kết nối WebSocket cho Wallet Status Updates

```javascript
// Kết nối WebSocket với token để nhận wallet status updates
const token = 'your_jwt_token_here';
const wsWallet = new WebSocket(`ws://172.25.67.101:8000/ws/wallet/${token}`);

// Khi kết nối thành công
wsWallet.onopen = () => {
  console.log('Connected to wallet status updates');
};

// Nhận messages từ server
wsWallet.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'connected') {
    console.log('WebSocket connected:', data.message);
  } else if (data.type === 'wallet_status_update') {
    // Cập nhật UI ngay lập tức khi có thay đổi trạng thái deposit
    handleWalletStatusUpdate(data);
  }
};

// Xử lý khi có lỗi
wsWallet.onerror = (error) => {
  console.error('WebSocket error:', error);
};

// Xử lý khi đóng kết nối
wsWallet.onclose = () => {
  console.log('WebSocket connection closed');
  // Có thể reconnect sau một khoảng thời gian
  setTimeout(() => {
    // Reconnect logic
  }, 3000);
};

// Hàm xử lý cập nhật trạng thái wallet
function handleWalletStatusUpdate(data) {
  if (data.event === 'deposit_activated') {
    // Deposit đã được activate
    const { transaction, wallet } = data;
    
    // Cập nhật trạng thái transaction trong danh sách
    updateTransactionStatus(transaction.id, {
      status: transaction.status,
      updated_at: transaction.updated_at
    });
    
    // Cập nhật số dư ví
    updateWalletBalance(wallet.balance, wallet.total_deposited);
    
    // Hiển thị thông báo thành công
    showNotification('success', data.message);
    
  } else if (data.event === 'deposit_rejected') {
    // Deposit đã bị reject
    const { transaction, wallet } = data;
    
    // Cập nhật trạng thái transaction trong danh sách
    updateTransactionStatus(transaction.id, {
      status: transaction.status,
      updated_at: transaction.updated_at
    });
    
    // Hiển thị thông báo từ chối
    showNotification('error', data.message);
  }
}

// Ví dụ hàm cập nhật UI
function updateTransactionStatus(transactionId, updates) {
  // Tìm transaction trong danh sách và cập nhật
  const transactionElement = document.querySelector(`[data-transaction-id="${transactionId}"]`);
  if (transactionElement) {
    // Cập nhật status badge
    const statusBadge = transactionElement.querySelector('.status-badge');
    statusBadge.textContent = updates.status;
    statusBadge.className = `status-badge status-${updates.status.toLowerCase()}`;
    
    // Cập nhật timestamp
    const timeElement = transactionElement.querySelector('.updated-time');
    timeElement.textContent = new Date(updates.updated_at).toLocaleString();
  }
}

function updateWalletBalance(balance, totalDeposited) {
  // Cập nhật số dư hiển thị trên UI
  const balanceElement = document.getElementById('wallet-balance');
  if (balanceElement) {
    balanceElement.textContent = formatCurrency(balance);
  }
  
  const totalDepositedElement = document.getElementById('total-deposited');
  if (totalDepositedElement) {
    totalDepositedElement.textContent = formatCurrency(totalDeposited);
  }
}
```

## 2. Kết nối WebSocket cho Notifications

```javascript
// Kết nối WebSocket với token để nhận notifications
const token = 'your_jwt_token_here';
const wsNotifications = new WebSocket(`ws://172.25.67.101:8000/ws/notifications/${token}`);

wsNotifications.onopen = () => {
  console.log('Connected to notifications');
};

wsNotifications.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'connected') {
    console.log('WebSocket connected:', data.message);
  } else if (data.type === 'notification') {
    // Nhận notification mới và hiển thị ngay lập tức
    handleNewNotification(data);
  }
};

wsNotifications.onerror = (error) => {
  console.error('WebSocket error:', error);
};

wsNotifications.onclose = () => {
  console.log('WebSocket connection closed');
};

function handleNewNotification(data) {
  // Thêm notification vào danh sách
  addNotificationToList({
    id: data.id,
    title: data.title,
    message: data.message,
    type: data.notification_type,
    is_unread: data.is_unread,
    created_at: data.created_at
  });
  
  // Hiển thị toast/alert notification
  showToastNotification(data);
  
  // Cập nhật badge số notification chưa đọc
  updateUnreadCount();
}
```

## 3. React Example với useEffect

```jsx
import { useEffect, useState, useRef } from 'react';

function WalletPage() {
  const [wallet, setWallet] = useState({ balance: 0, totalDeposited: 0 });
  const [transactions, setTransactions] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const ws = new WebSocket(`ws://172.25.67.101:8000/ws/wallet/${token}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'wallet_status_update') {
        if (data.event === 'deposit_activated') {
          // Cập nhật transaction trong state
          setTransactions(prev => prev.map(tx =>
            tx.id === data.transaction.id
              ? { ...tx, ...data.transaction }
              : tx
          ));

          // Cập nhật wallet balance
          setWallet({
            balance: data.wallet.balance,
            totalDeposited: data.wallet.total_deposited,
            totalSpent: data.wallet.total_spent
          });

          // Hiển thị toast notification
          toast.success(data.message);
        } else if (data.event === 'deposit_rejected') {
          // Cập nhật transaction status
          setTransactions(prev => prev.map(tx =>
            tx.id === data.transaction.id
              ? { ...tx, status: data.transaction.status }
              : tx
          ));

          toast.error(data.message);
        }
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket closed');
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div>
      <div>Balance: {wallet.balance}</div>
      <div>Total Deposited: {wallet.totalDeposited}</div>
      {/* Transaction list */}
    </div>
  );
}
```

## 4. Message Format

### Wallet Status Update
```json
{
  "type": "wallet_status_update",
  "event": "deposit_activated" | "deposit_rejected",
  "transaction": {
    "id": "uuid",
    "status": "SUCCESS" | "FAILED" | "PENDING",
    "amount": 100000,
    "bank_name": "Vietcombank",
    "bank_account": "1234567890",
    "transfer_code": "ABC123",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "wallet": {
    "balance": 500000,
    "total_deposited": 1000000,
    "total_spent": 500000
  },
  "message": "Deposit transaction has been activated successfully",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Notification
```json
{
  "type": "notification",
  "id": "uuid",
  "title": "Notification Title",
  "message": "Notification message",
  "notification_type": "SUCCESS" | "WARNING" | "ERROR",
  "is_unread": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 5. WebSocket cho Admin - Nhận Deposit Requests

### Kết nối WebSocket cho Admin

```javascript
// Admin kết nối WebSocket để nhận deposit requests mới
const adminToken = 'admin_jwt_token_here';
const wsAdminDeposits = new WebSocket(`ws://172.25.67.101:8000/ws/admin/deposits/${adminToken}`);

// Hoặc dùng notifications endpoint (cũng hoạt động)
const wsAdminNotifications = new WebSocket(`ws://172.25.67.101:8000/ws/notifications/${adminToken}`);

wsAdminDeposits.onopen = () => {
  console.log('Admin connected to deposit requests');
};

wsAdminDeposits.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'connected') {
    console.log('Admin WebSocket connected:', data.message);
  } else if (data.type === 'new_deposit_request') {
    // Nhận deposit request mới từ user
    handleNewDepositRequest(data);
  }
};

wsAdminDeposits.onerror = (error) => {
  console.error('WebSocket error:', error);
};

wsAdminDeposits.onclose = () => {
  console.log('Admin WebSocket connection closed');
};

function handleNewDepositRequest(data) {
  // Hiển thị notification/toast
  showNotification('warning', data.message);
  
  // Thêm deposit request mới vào danh sách
  addDepositToList({
    id: data.transaction.id,
    user: data.user,
    amount: data.transaction.amount,
    bank_name: data.transaction.bank_name,
    transfer_code: data.transaction.transfer_code,
    status: data.transaction.status,
    created_at: data.transaction.created_at
  });
  
  // Cập nhật badge số deposit pending
  updatePendingDepositsCount();
  
  // Hiển thị notification trong notification panel
  addNotificationToPanel(data.notification);
}

// Ví dụ với React
function AdminDashboard() {
  const [deposits, setDeposits] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('adminToken');
    const ws = new WebSocket(`ws://172.25.67.101:8000/ws/admin/deposits/${token}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'new_deposit_request') {
        // Thêm deposit mới vào danh sách
        setDeposits(prev => [data.transaction, ...prev]);
        
        // Thêm notification
        setNotifications(prev => [data.notification, ...prev]);
        
        // Hiển thị toast
        toast.warning(data.message);
        
        // Cập nhật số lượng pending
        updatePendingCount();
      }
    };

    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div>
      <div>Pending Deposits: {deposits.filter(d => d.status === 'PENDING').length}</div>
      {/* Deposit list */}
      {/* Notification panel */}
    </div>
  );
}
```

### New Deposit Request Message Format

```json
{
  "type": "new_deposit_request",
  "event": "deposit_created",
  "transaction": {
    "id": "uuid",
    "status": "PENDING",
    "amount": 100000,
    "bank_name": "Vietcombank",
    "bank_account": "1234567890",
    "transfer_code": "ABC123",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "user": {
    "id": "uuid",
    "name": "User Name",
    "email": "user@example.com"
  },
  "notification": {
    "id": "uuid",
    "title": "Yêu cầu nạp tiền mới",
    "message": "User User Name (user@example.com) đã yêu cầu nạp 100,000 VNĐ",
    "type": "WARNING",
    "is_unread": true,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "message": "User User Name đã yêu cầu nạp tiền",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Lưu ý

1. **Token Authentication**: Luôn sử dụng JWT token hợp lệ trong URL
2. **Reconnection**: Nên implement logic reconnect khi connection bị đóng
3. **Error Handling**: Luôn xử lý lỗi và có fallback mechanism
4. **State Management**: Cập nhật state ngay khi nhận được message để UI refresh ngay lập tức
5. **Admin Endpoints**: Admin có thể dùng cả `/ws/admin/deposits/{token}` hoặc `/ws/notifications/{token}` để nhận updates

