"""
合成数据：订单处理脚本（面向对象重构版）
所有数据均为虚构，仅供演示。

重构说明（相对 legacy_orders.py）：
- 职责分离：Product / Customer / Order 为领域模型（数据 + 领域逻辑），
  OrderProcessor 负责数据仓库与查询/聚合，ReportGenerator 负责报告与导出。
- 消除重复代码：原 calc_order_total 与 calc_order_total_v2 两份重复实现
  合并为 Order.total(product, customer) 单一实现，供所有调用方复用。
- 行为完全一致：相同输入产生相同输出（format_report / export_json / 各查询函数）。
- 模块级函数接口与 legacy_orders.py 保持一致，便于直接替换调用。
"""

import json
from dataclasses import dataclass
from datetime import datetime

# ---- 合成演示数据（与 legacy_orders.py 完全一致） ----

_ORDERS_DATA = [
    {"id": "O1001", "customer_id": "C001", "product_id": "P001", "qty": 2, "date": "2024-08-01", "status": "pending"},
    {"id": "O1002", "customer_id": "C002", "product_id": "P002", "qty": 1, "date": "2024-08-02", "status": "shipped"},
    {"id": "O1003", "customer_id": "C001", "product_id": "P003", "qty": 5, "date": "2024-08-03", "status": "delivered"},
    {"id": "O1004", "customer_id": "C003", "product_id": "P001", "qty": 1, "date": "2024-08-04", "status": "pending"},
    {"id": "O1005", "customer_id": "C002", "product_id": "P004", "qty": 3, "date": "2024-08-05", "status": "cancelled"},
    {"id": "O1006", "customer_id": "C004", "product_id": "P002", "qty": 2, "date": "2024-08-06", "status": "shipped"},
    {"id": "O1007", "customer_id": "C001", "product_id": "P005", "qty": 1, "date": "2024-08-07", "status": "pending"},
    {"id": "O1008", "customer_id": "C003", "product_id": "P003", "qty": 2, "date": "2024-08-08", "status": "delivered"},
]

_PRODUCTS_DATA = {
    "P001": {"name": "无线鼠标 Alpha", "price": 129.00, "category": "外设"},
    "P002": {"name": "机械键盘 Pro", "price": 499.00, "category": "外设"},
    "P003": {"name": "USB-C 扩展坞", "price": 259.00, "category": "配件"},
    "P004": {"name": "降噪耳机 X1", "price": 899.00, "category": "音频"},
    "P005": {"name": "4K 显示器 Ultra", "price": 2499.00, "category": "显示"},
}

_CUSTOMERS_DATA = {
    "C001": {"name": "张三", "level": "gold", "region": "华东"},
    "C002": {"name": "李四", "level": "silver", "region": "华北"},
    "C003": {"name": "王五", "level": "bronze", "region": "华南"},
    "C004": {"name": "赵六", "level": "gold", "region": "华西"},
}

# 客户等级折扣（未列出的等级不打折，与 legacy 行为一致）
_LEVEL_DISCOUNTS = {
    "gold": 0.85,
    "silver": 0.90,
    "bronze": 0.95,
}


# ---- 领域模型 ----

@dataclass
class Product:
    """商品：编号、名称、单价、分类。"""

    product_id: str
    name: str
    price: float
    category: str


@dataclass
class Customer:
    """客户：编号、姓名、等级、地区。"""

    customer_id: str
    name: str
    level: str
    region: str

    def discount_rate(self) -> float:
        """客户等级对应的折扣率；未匹配等级返回 1.0（不打折）。"""
        return _LEVEL_DISCOUNTS.get(self.level, 1.0)


@dataclass
class Order:
    """订单：编号、客户、商品、数量、日期、状态。"""

    order_id: str
    customer_id: str
    product_id: str
    qty: int
    date: str
    status: str

    def total(self, product: Product, customer: Customer) -> float:
        """订单金额 = 单价 × 数量 × 客户等级折扣。

        统一金额计算入口，消除 legacy 中 calc_order_total /
        calc_order_total_v2 的重复实现。
        """
        total = product.price * self.qty
        total *= customer.discount_rate()
        return round(total, 2)

    def to_dict(self):
        """与 legacy 原始订单字典兼容的序列化形式。"""
        return {
            "id": self.order_id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "qty": self.qty,
            "date": self.date,
            "status": self.status,
        }


# ---- 数据仓库与查询/聚合 ----

class OrderProcessor:
    """负责数据的加载、存储、查询与聚合。"""

    def __init__(self):
        self.orders = []
        self.products = {}
        self.customers = {}

    def load_data(self):
        """加载合成演示数据（可重复调用，会重置状态）。"""
        self.orders = [
            Order(
                order_id=o["id"],
                customer_id=o["customer_id"],
                product_id=o["product_id"],
                qty=o["qty"],
                date=o["date"],
                status=o["status"],
            )
            for o in _ORDERS_DATA
        ]
        self.products = {pid: Product(pid, **p) for pid, p in _PRODUCTS_DATA.items()}
        self.customers = {cid: Customer(cid, **c) for cid, c in _CUSTOMERS_DATA.items()}

    def get_order(self, order_id):
        """按订单编号查找订单；不存在返回 None。"""
        for o in self.orders:
            if o.order_id == order_id:
                return o
        return None

    def _order_total(self, order: Order) -> float:
        """计算指定订单对象的金额（内部统一实现）。"""
        return order.total(self.products[order.product_id], self.customers[order.customer_id])

    def order_total(self, order_id: str) -> float:
        """按订单编号计算金额；未知订单返回 0.0（与 legacy 一致）。"""
        order = self.get_order(order_id)
        if order is None:
            return 0.0
        return self._order_total(order)

    def get_customer_orders(self, customer_id):
        """某客户的全部订单明细。"""
        result = []
        for o in self.orders:
            if o.customer_id == customer_id:
                result.append({
                    "order_id": o.order_id,
                    "product": self.products[o.product_id].name,
                    "qty": o.qty,
                    "total": self._order_total(o),
                    "status": o.status,
                })
        return result

    def get_product_sales(self, product_id):
        """某商品的销量与收入汇总。"""
        total_qty = 0
        total_revenue = 0.0
        for o in self.orders:
            if o.product_id == product_id:
                total_qty += o.qty
                total_revenue += self._order_total(o)
        return {"product_id": product_id, "total_qty": total_qty, "total_revenue": round(total_revenue, 2)}

    def get_region_summary(self):
        """按地区汇总订单数与收入。"""
        region_data = {}
        for o in self.orders:
            region = self.customers[o.customer_id].region
            if region not in region_data:
                region_data[region] = {"order_count": 0, "revenue": 0.0}
            region_data[region]["order_count"] += 1
            region_data[region]["revenue"] += self._order_total(o)
        for r in region_data:
            region_data[r]["revenue"] = round(region_data[r]["revenue"], 2)
        return region_data

    def get_pending_orders(self):
        """状态为 pending 的订单列表（保持原始顺序）。"""
        return [o for o in self.orders if o.status == "pending"]


# ---- 报告与导出 ----

class ReportGenerator:
    """负责生成文本报告与 JSON 导出。"""

    def __init__(self, processor: OrderProcessor):
        self.processor = processor

    def format_report(self):
        """生成与 legacy 完全一致的文本报告。"""
        p = self.processor
        lines = []
        lines.append("=" * 40)
        lines.append("订单处理报告（合成数据）")
        lines.append("=" * 40)
        lines.append(f"生成时间: {datetime.now().isoformat()}")
        lines.append(f"总订单数: {len(p.orders)}")
        lines.append("")
        lines.append("--- 按客户汇总 ---")
        for cid, customer in p.customers.items():
            corders = p.get_customer_orders(cid)
            lines.append(f"客户 {customer.name} ({cid}): {len(corders)} 笔订单")
            for co in corders:
                lines.append(f"  {co['order_id']}: {co['product']} x{co['qty']} = {co['total']} 元 [{co['status']}]")
        lines.append("")
        lines.append("--- 按地区汇总 ---")
        region_summary = p.get_region_summary()
        for region, data in region_summary.items():
            lines.append(f"{region}: {data['order_count']} 笔订单, 收入 {data['revenue']} 元")
        lines.append("")
        lines.append("--- 按产品汇总 ---")
        for pid in p.products:
            sales = p.get_product_sales(pid)
            lines.append(f"{pid}: 销量 {sales['total_qty']}, 收入 {sales['total_revenue']} 元")
        lines.append("")
        lines.append("--- 待处理订单 ---")
        for po in p.get_pending_orders():
            total = p.order_total(po.order_id)
            lines.append(f"{po.order_id}: {p.products[po.product_id].name} = {total} 元")
        lines.append("=" * 40)
        return "\n".join(lines)

    def save_report(self, path="report.txt"):
        """将文本报告写入文件。"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.format_report())
        print(f"报告已保存到 {path}")

    def export_json(self, path="orders.json"):
        """将订单数据导出为 JSON 文件。"""
        p = self.processor
        data = []
        for o in p.orders:
            data.append({
                "order_id": o.order_id,
                "customer": p.customers[o.customer_id].name,
                "product": p.products[o.product_id].name,
                "quantity": o.qty,
                "total": p.order_total(o.order_id),
                "status": o.status,
                "date": o.date,
            })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"JSON 已导出到 {path}")


# ---- 模块级兼容接口（与 legacy_orders.py 调用方式一致） ----

_processor = OrderProcessor()
_report = ReportGenerator(_processor)


def load_data():
    _processor.load_data()


def calc_order_total(order_id):
    return _processor.order_total(order_id)


def get_customer_orders(customer_id):
    return _processor.get_customer_orders(customer_id)


def get_product_sales(product_id):
    return _processor.get_product_sales(product_id)


def get_region_summary():
    return _processor.get_region_summary()


def get_pending_orders():
    return _processor.get_pending_orders()


def format_report():
    return _report.format_report()


def save_report(path="report.txt"):
    _report.save_report(path)


def export_json(path="orders.json"):
    _report.export_json(path)


if __name__ == "__main__":
    load_data()
    print(format_report())
    save_report()
    export_json()
