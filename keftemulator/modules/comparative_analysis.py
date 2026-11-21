"""Comparative Analysis - Intelligence Comparison & Benchmarking"""

class ComparativeAnalysis:
    name = "Comparative Analysis"
    category = "Intelligence"
    accepts = ["*"]
    
    def investigate(self, target, ctx):
        try:
            ctx.emit("status", "Performing comparative analysis")
            ctx.emit("link", "Target Comparison", "Compare multiple targets",
                    {"feature": "targets"}, rel="comp_targets")
            ctx.emit("link", "Threat Comparison", "Compare threat levels",
                    {"feature": "threats"}, rel="comp_threats")
            ctx.emit("link", "Trend Comparison", "Compare trend patterns",
                    {"feature": "trends"}, rel="comp_trends")
            ctx.emit("link", "Benchmarking", "Benchmark against industry",
                    {"feature": "benchmark"}, rel="comp_benchmark")
        except Exception as e:
            ctx.emit("link", "Comparative Error", str(e)[:100], {"error": str(e)}, rel="analytics_error")

MODULE = ComparativeAnalysis()
