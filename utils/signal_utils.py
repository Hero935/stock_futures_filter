import os
import yaml


class SignalEvaluator:
    def __init__(self, filename="signals.yaml"):
        self.filename = filename
        self.config = self.load_yaml_config()

    def load_yaml_config(self):
        """讀取 YAML 設定"""
        if os.path.exists(self.filename):
            with open(self.filename, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        return {"buy_signal": {"conditions": []}, "sell_signal": {"conditions": []}}

    def save_yaml_config(self):
        """儲存 YAML 設定"""
        with open(self.filename, "w", encoding="utf-8") as file:
            yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)

    def evaluate_condition(self, condition, row):
        """根據條件進行比較"""
        # 解析條件格式，例如："MACD_Diff: < 0" 轉換為 key、operator 和 value
        key, operator_value = list(condition.items())[0]
        operator, value = operator_value.split()

        # 轉換條件中的 value 為數字
        value = float(value)

        # 根據不同的運算符進行比較
        if operator == ">":
            return row[key] > value
        elif operator == "<":
            return row[key] < value
        elif operator == "=":
            return row[key] == value
        else:
            return False

    def evaluate_logic(self, logic, row):
        """根據邏輯條件進行遞歸評估"""
        if "or" in logic:
            # 如果是 "or" 條件，任何一個條件為真就返回真
            return any(self.evaluate_logic(cond, row) for cond in logic["or"])
        elif "and" in logic:
            # 如果是 "and" 條件，所有條件必須為真
            return all(self.evaluate_logic(cond, row) for cond in logic["and"])
        else:
            # 如果是基本條件，直接評估
            return self.evaluate_condition(logic, row)

    def is_buy_signal(self, row):
        """判斷是否為買入信號"""
        return self.evaluate_logic(self.config["buy_signal"], row)

    def is_sell_signal(self, row):
        """判斷是否為賣出信號"""
        return self.evaluate_logic(self.config["sell_signal"], row)
