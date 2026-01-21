"""
A minimal, runnable CTA strategy template.

Usage (high level):
1. Place this file under your runtime folder's `strategies` directory.
2. Ensure vnpy_ctastrategy is installed and the strategy is registered/loaded by
   your CTA engine (UI or no_ui example).
3. Create a strategy instance with your vt_symbol and parameters.
"""

from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class SimpleMaCtaStrategy(CtaTemplate):
    """Simple moving-average crossover CTA strategy."""

    author = "vn.py user"

    fast_window = 10
    slow_window = 30
    fixed_size = 1

    fast_ma = 0.0
    slow_ma = 0.0

    parameters = ["fast_window", "slow_window", "fixed_size"]
    variables = ["fast_ma", "slow_ma"]

    def __init__(
        self,
        cta_engine,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ) -> None:
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(self.on_bar)
        self.am = ArrayManager(size=max(self.fast_window, self.slow_window) + 5)

    def on_init(self) -> None:
        self.write_log("策略初始化")
        self.load_bar(10)

    def on_start(self) -> None:
        self.write_log("策略启动")

    def on_stop(self) -> None:
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        self.bg.update_bar(bar)
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self.fast_ma = self.am.sma(self.fast_window)
        self.slow_ma = self.am.sma(self.slow_window)

        if self.fast_ma > self.slow_ma and self.pos <= 0:
            self.cover(bar.close_price, abs(self.pos))
            self.buy(bar.close_price, self.fixed_size)
        elif self.fast_ma < self.slow_ma and self.pos >= 0:
            self.sell(bar.close_price, abs(self.pos))
            self.short(bar.close_price, self.fixed_size)

        self.put_event()

    def on_order(self, order: OrderData) -> None:
        pass

    def on_trade(self, trade: TradeData) -> None:
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        pass
