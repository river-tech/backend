from enum import Enum

class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class WorkflowStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"

class PurchaseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PENDING = "PENDING"
    REJECT = "REJECT"

class PaymentMethod(str, Enum):
    QR = "QR"

class NotificationType(str, Enum):
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"     # nạp token vào ví
    PURCHASE = "PURCHASE"   # trừ token khi mua workflow
    REFUND = "REFUND"       # hoàn token

class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
