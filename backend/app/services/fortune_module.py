from app.services.report_generator import cultural_wealth_reference, living_recommendations, metric_explanations


def get_fortune_placeholder(scores: dict | None = None, terrain_metrics: dict | None = None) -> dict:
    """返回文化娱乐模块占位和民俗招财倾向说明，不做真实命运/财运预测。"""
    base = {
        "enabled": False,
        "message": "命运、财运、吉凶预测模块属于后续文化娱乐功能，当前 MVP 暂未开放。",
        "disclaimer": "该模块未来仅作为传统民俗文化娱乐参考，不构成现实人生、投资、婚姻、医疗、法律或商业决策建议。",
    }
    if not scores or not terrain_metrics:
        return base

    wealth_reference = cultural_wealth_reference(scores, terrain_metrics)
    return {
        **base,
        "wealth_reference": wealth_reference,
        "living_recommendations": living_recommendations(terrain_metrics, scores),
        "metric_explanations": metric_explanations(),
    }
