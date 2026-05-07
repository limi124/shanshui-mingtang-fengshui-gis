from typing import Any

import httpx


def generate_llm_report(
    *,
    llm_enabled: bool,
    api_key: str,
    base_url: str,
    model: str,
    fence_info: dict[str, Any],
    terrain_metrics: dict[str, Any],
    spatial_pattern: dict[str, str],
    scores: dict[str, int],
    data_status: dict[str, dict[str, Any]],
    fallback_report: str,
) -> dict[str, Any]:
    """Generate an AI interpretation from local GIS analysis results.

    Raw fence GeoJSON and exact center coordinates are intentionally excluded
    from the LLM payload to reduce exposure of sensitive location data.
    """
    if not llm_enabled or not api_key or not base_url or not model:
        return {
            "enabled": False,
            "used": False,
            "provider": "local_template",
            "message": "LLM 未启用或配置不完整，当前使用本地模板报告。",
            "content": fallback_report,
        }

    payload_for_llm = {
        "fence_summary": {
            "area_m2": fence_info["area_m2"],
            "vertex_count": fence_info["vertex_count"],
        },
        "terrain_metrics": terrain_metrics,
        "spatial_pattern": spatial_pattern,
        "scores": scores,
        "data_status": {
            "dem": _public_status(data_status.get("dem", {})),
            "water": _public_status(data_status.get("water", {})),
            "road": _public_status(data_status.get("road", {})),
        },
    }

    try:
        response = httpx.post(
            _chat_url(base_url),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": _system_prompt()},
                    {"role": "user", "content": _user_prompt(payload_for_llm)},
                ],
                "temperature": 0.65,
                "max_tokens": 1800,
            },
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        return {
            "enabled": True,
            "used": True,
            "provider": "openai_compatible",
            "model": model,
            "message": "已基于本地 GIS 指标调用 AI 生成风水文化解读。",
            "content": content,
        }
    except Exception as exc:
        return {
            "enabled": True,
            "used": False,
            "provider": "local_template",
            "model": model,
            "message": f"AI 解读调用失败，已回退本地模板报告：{exc}",
            "content": fallback_report,
        }


def _chat_url(base_url: str) -> str:
    clean = base_url.rstrip("/")
    if clean.endswith("/chat/completions"):
        return clean
    return f"{clean}/chat/completions"


def _public_status(status: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in status.items()
        if key not in {"path", "file_path", "source_path"}
    }


def _system_prompt() -> str:
    return (
        "你是一个 WebGIS 风水地理智能分析系统的报告生成助手。"
        "你必须只依据用户提供的 GIS 指标、DEM 地形指标、水系关系、坡向坡度和规则评分进行解读。"
        "不要虚构不存在的河流、道路、山体、建筑或地名。"
        "不要输出原始坐标，不要要求上传敏感地块位置。"
        "表达风格可以更有传统风水文化吸引力，突出靠山、明堂、藏风、得水、纳气、聚财象意。"
        "但必须明确：聚财、旺财、吉凶等内容仅为传统民俗文化娱乐参考，不代表真实财富、收入、投资或经营结果。"
        "不得出现必然发财、保证转运、百分百大吉、改变命运等绝对化承诺。"
        "同时给出现代地理解释和风险提示。"
    )


def _user_prompt(payload: dict[str, Any]) -> str:
    return (
        "请基于以下结构化 GIS 分析结果，生成一份中文风水地理解读报告。\n"
        "报告结构：\n"
        "1. 一句话吸引人的总体判断\n"
        "2. 靠山格局\n"
        "3. 明堂与纳气\n"
        "4. 水系与得水生财象意\n"
        "5. 坡向采光与人居舒适度\n"
        "6. 聚财格局文化参考\n"
        "7. 这个地块的人应该怎么做\n"
        "8. 现代地理风险提示\n"
        "9. 免责声明\n\n"
        "注意：如果某个数据状态为 missing 或 placeholder，要明确说明不可做确定性判断。\n"
        "以下是后端本地 GIS 计算结果，不包含原始围栏坐标：\n"
        f"{payload}"
    )
