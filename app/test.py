from core import VannaService
import pandas as pd

def train_data(vs:VannaService):
        # 使用DDL（数据定义语言）训练
    ddl = """
    CREATE TABLE IF NOT EXISTS customers (
        `customer_id` INT(11) AUTO_INCREMENT PRIMARY KEY comment '客户唯一标识',
        `name` VARCHAR(100) comment '客户姓名',
        `email` VARCHAR(100) comment '客户邮箱',
        `signup_date` DATE comment '客户注册日期'
    ) comment '客户表';
    
    CREATE TABLE IF NOT EXISTS orders (
        `order_id` INT(11) AUTO_INCREMENT PRIMARY KEY comment '订单唯一标识',
        `customer_id` INT(11) comment '关联客户表的外键',
        `order_date` DATE comment '订单日期',
        `total_amount` DECIMAL(10,2) comment '订单总金额',
        FOREIGN KEY (`customer_id`) REFERENCES customers(`customer_id`)
    ) comment '订单表';
    """
    res = vs.train(ddl=ddl)
    print(res)

    # 使用文档训练
    doc = """
    我们的业务定义'活跃客户'为在过去30天内下过订单的客户。'总销售额'指的是所有订单金额的总和，不包括税和运费。
    """
    res = vs.train(documentation=doc)
    print(res)

    # 使用现有SQL查询训练
    sql = """
    SELECT c.name, SUM(o.total_amount) as total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.name
    ORDER BY total_spent DESC
    LIMIT 10
    """
    res = vs.train(sql=sql)
    print(res)

    # 从自然语言生成SQL
    sql = vs.generate_sql("谁是总订单金额最高的前10位客户？")
    print(sql)

    # 提问并直接获取结果
    res = vs.ask("谁是总订单金额最高的前10位客户？")
    print(res)

def clear_data(vs:VannaService):
    res:pd.DataFrame = vs.get_training_data()
    # 获取id列的所有值
    ids = res["id"].tolist()
    for id in ids:
        vs.remove_training_data(id)

def run_sql(vs:VannaService,sql:str):
    res = vs.run_sql(sql)
    print(res)

if __name__ == "__main__":
    vs = VannaService()
    sql = """
    select * from customers
    """
    run_sql(vs,sql)
    # train_data(vs)
    # clear_data(vs)
