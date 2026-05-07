DISCLAIMER = (
    "本系统基于地理空间数据、DEM地形分析和传统风水文化解释生成报告，仅用于环境格局分析、"
    "传统文化研究与娱乐参考，不构成现实人生、投资、医疗、婚姻、法律、商业选址等决策建议。"
)


def metric_explanations() -> dict[str, str]:
    return {
        "mean_elevation": "平均高程用于描述地块整体所处的海拔水平，可辅助判断场地排水、视野和周边地势关系。",
        "relief": "相对高差反映地块内部最高点与最低点差异，高差适中通常利于形成层次，过大则需关注边坡和排水。",
        "mean_slope": "平均坡度反映地表倾斜程度，缓坡通常更利于建设和步行，陡坡需要重点复核稳定性。",
        "dominant_aspect": "主要坡向影响日照、采光、风向和湿度条件，偏南、东南、西南通常具有较好的日照潜力。",
        "terrain_roughness": "地形粗糙度反映地表起伏复杂程度，越高说明地形越破碎，工程整理和排水组织越需要谨慎。",
        "back_mountain_score": "靠山格局评分描述后方或北侧是否具有相对稳定的地势支撑，现代解释可理解为边界、防风和背景地形条件。",
        "front_open_score": "明堂开阔评分描述前方空间是否舒展，现代解释对应视野、活动面和场地使用弹性。",
        "enclosure_score": "藏风围合评分描述左右两侧是否有适度围合，强调边界感和风环境，不代表现实吉凶断语。",
        "water_score": "得水条件评分描述水体、汇水路径与场地的关系。从传统风水语境看，“水”常被借喻为流动、生机与财气；现代解释则对应亲水环境、排水安全和洪涝约束。",
        "aspect_light_score": "坡向采光评分描述坡向带来的日照潜力，仍需结合建筑物、树木和山体遮挡复核。",
        "terrain_stability_score": "地形稳定评分综合坡度、高差和粗糙度，提示建设适宜性和潜在地质风险。",
    }


def living_recommendations(terrain_metrics: dict, scores: dict) -> list[str]:
    recommendations = []
    if terrain_metrics["mean_slope"] <= 10:
        recommendations.append("场地平均坡度较缓，可优先保持现有缓坡台地形态，避免大挖大填。")
    else:
        recommendations.append("场地坡度偏大，建议先做边坡稳定、挡墙和雨水排放专项复核。")

    if terrain_metrics["dominant_aspect"] in {"南", "东南", "西南"}:
        recommendations.append("主要坡向具备较好的采光潜力，住宅主要活动空间可优先考虑朝向开阔和日照较好的方向。")
    else:
        recommendations.append("主要坡向的日照优势不明显，建议通过开窗朝向、院落开口和遮挡复核改善采光。")

    if scores["front_open_score"] >= 75:
        recommendations.append("前场开阔度较好，传统上可理解为“明堂舒展、纳气有余”；建议保留门前或院前开敞空间，不宜用高墙、密植或杂物过度遮挡。")
    else:
        recommendations.append("前场开阔度一般，可通过整理前方空地、控制围墙高度和优化出入口视线，增强“纳气入口”和空间舒展感。")

    if scores["water_score"] <= 60:
        recommendations.append("得水条件偏弱或需复核，建议补充河流、沟渠、排水口和暴雨汇流路径；传统上讲“水聚则气聚”，现代上则应优先避免低洼积水。")
    else:
        recommendations.append("已识别到水系关系，可将其作为“得水有源”的文化参考，但实际使用仍要核验洪水位、退让红线和排水安全。")

    recommendations.append("若希望强化“聚气聚财”的空间感，可优先做到前场整洁、入口顺畅、水路清明、背后稳定；现实层面仍以排水、采光、通风、道路和结构安全为先。")
    return recommendations


def cultural_wealth_reference(scores: dict, terrain_metrics: dict) -> dict[str, str | int | list[str]]:
    """民俗文化娱乐解释，不做真实财运预测。"""
    wealth_score = round(
        scores["front_open_score"] * 0.28
        + scores["water_score"] * 0.22
        + scores["back_mountain_score"] * 0.18
        + scores["enclosure_score"] * 0.16
        + scores["aspect_light_score"] * 0.16
    )
    if wealth_score >= 80:
        tendency = "从传统民俗语境看，该地块具备较鲜明的“明堂纳气、藏风聚气、得水生财”象意，属于较有吸引力的聚财格局参考。"
    elif wealth_score >= 65:
        tendency = "从传统民俗语境看，该地块具备一定“纳气聚财”的基础，若进一步整理明堂、水路和左右围合，文化观感会更完整。"
    else:
        tendency = "从传统民俗语境看，该地块当前“纳气、聚气、得水”的表现偏普通，建议先从入口、明堂、排水和采光整理入手，逐步提升聚财象意。"

    interpretation = _wealth_interpretation(scores, terrain_metrics, wealth_score)

    actions = [
        "保持门前和院前整洁开阔，形成“明堂亮、气口顺”的第一印象，减少杂物堆放与动线阻塞。",
        "优先处理排水沟、雨水口和低洼积水点，让水路清楚、流向有序，避免湿气和径流长期滞留。",
        "保留适度绿化和边界围合，营造“藏风不闭塞”的空间感，但不要封死主要采光、通风和视线通道。",
        "入口、院落和主要活动面宜保持明亮、干净、可达，传统上更容易形成“纳气入宅”的文化观感。",
        "若用于经营或办公，应以真实客流、交通、消防、产权和市场调研作为决策依据。",
    ]
    if terrain_metrics["mean_slope"] > 15:
        actions.insert(0, "陡坡区域不宜只看文化寓意，应先完成工程安全和地质风险评估。")

    return {
        "enabled": True,
        "wealth_culture_score": wealth_score,
        "title": "民俗聚财格局参考",
        "tendency": tendency,
        "interpretation": interpretation,
        "actions": actions,
        "disclaimer": "以上仅为传统风水民俗与空间文化娱乐解读，不代表真实财运、收入或经营结果预测，不构成投资、经营、购房或商业选址建议。",
    }


def _wealth_interpretation(scores: dict, terrain_metrics: dict, wealth_score: int) -> list[dict[str, str]]:
    if wealth_score >= 80:
        overall = (
            "整体来看，该地块在传统风水文化中可归入“气口较顺、明堂有承、水气有源”的类型。"
            "它的吸引力不在于单一指标很高，而在于靠山、明堂、得水、采光几项之间形成了较完整的空间叙事。"
        )
    elif wealth_score >= 65:
        overall = (
            "整体来看，该地块具备一定聚财格局基础，属于“有气可纳、有局可调”的类型。"
            "当前格局不是强烈的富贵断语，而是更适合通过入口、明堂、水路和边界整理，把空间气象慢慢做顺。"
        )
    else:
        overall = (
            "整体来看，该地块的聚财象意仍处在可塑阶段，当前更像“底子可整理、格局待打开”的状态。"
            "与其急于判断旺衰，不如先把明堂、入口、排水、采光和动线这些基础条件处理好。"
        )

    front_text = (
        "明堂代表地块前方的承接面和视野展开。当前明堂评分越高，越适合保留开阔、明亮、干净的前场，"
        "传统上容易形成“气从前来、缓缓入局”的观感；如果明堂偏弱，就要避免门前杂乱、围挡过高和出入口拥堵。"
    )
    water_text = (
        "水在传统语境中常被借喻为财气流动。若水系距离适中、流向清楚，可作为“得水有源”的文化亮点；"
        "若水体与地块相交或过近，则不能只按吉象理解，还要优先核验洪水位、退让红线、潮湿积水和排水组织。"
    )
    enclosure_text = (
        "藏风聚气强调左右边界和后方支撑的稳定感。适度围合会让场地有收束感，过度封闭则会压缩采光、通风和视线。"
        "更理想的做法是背后稳定、左右有护、前方开敞，让空间既能聚住气，也不显得逼仄。"
    )
    action_text = (
        "如果希望提升“纳气聚财”的文化观感，优先顺序建议是：先清入口，再亮明堂，再理水路，最后补绿化和边界。"
        "这些动作不会带来真实财运保证，但会实实在在改善空间秩序、识别度、舒适度和使用体验。"
    )
    if terrain_metrics["mean_slope"] > 15:
        action_text += " 由于坡度偏大，还应把边坡稳定和雨水径流放在所有文化整理之前。"

    return [
        {"title": "总体聚财象意", "content": overall},
        {"title": "明堂纳气", "content": front_text},
        {"title": "得水生财", "content": water_text},
        {"title": "藏风聚气", "content": enclosure_text},
        {"title": "整理建议", "content": action_text},
    ]


def generate_report(fence_info: dict, terrain_metrics: dict, spatial_pattern: dict, scores: dict) -> str:
    """根据结构化 GIS 分析结果生成克制的中文报告，不调用外部大模型。"""
    explanations = metric_explanations()
    recommendations = living_recommendations(terrain_metrics, scores)
    wealth_reference = cultural_wealth_reference(scores, terrain_metrics)

    risk_notes = []
    if terrain_metrics["mean_slope"] > 15:
        risk_notes.append("平均坡度偏大，后续建设需重点复核边坡稳定性和排水组织。")
    if terrain_metrics["min_elevation"] < terrain_metrics["mean_elevation"] - terrain_metrics["relief"] * 0.35:
        risk_notes.append("局部低洼位置可能存在汇水或积水风险，建议结合暴雨径流数据复核。")
    if not risk_notes:
        risk_notes.append("当前 mock 指标显示整体坡度适中，但正式结论仍需真实 DEM 与现场核验。")

    return "\n\n".join(
        [
            "一、用户圈定范围基本信息\n"
            f"本次分析范围面积约 {fence_info['area_m2']} 平方米，中心点为 "
            f"{fence_info['center_lon']}, {fence_info['center_lat']}，围栏顶点数 {fence_info['vertex_count']} 个。",
            "二、核心指标意义说明\n"
            f"平均高程：{explanations['mean_elevation']}\n"
            f"相对高差：{explanations['relief']}\n"
            f"平均坡度：{explanations['mean_slope']}\n"
            f"主要坡向：{explanations['dominant_aspect']}\n"
            f"地形稳定：{explanations['terrain_stability_score']}",
            "三、地形环境概况\n"
            f"范围内平均高程约 {terrain_metrics['mean_elevation']} 米，高程区间为 "
            f"{terrain_metrics['min_elevation']} 至 {terrain_metrics['max_elevation']} 米，"
            f"相对高差约 {terrain_metrics['relief']} 米，地形位置类型判断为“{terrain_metrics['terrain_position']}”。",
            "四、山势与靠山格局分析\n"
            f"{spatial_pattern['back_mountain']} 从传统风水文化视角看，后方相对抬升常被解释为背靠；"
            "从现代地理角度看，它也可能影响风场、排水方向和建设边界。",
            "五、明堂开阔度分析\n"
            f"{spatial_pattern['front_open']} 现代空间评价中，这对应视域展开、坡面舒缓度和场地使用弹性。",
            "六、左右围合与藏风格局分析\n"
            f"{spatial_pattern['left_right_enclosure']} 该指标用于描述场地边界的包裹感，不代表任何现实吉凶判断。",
            "七、水系与得水生财象意分析\n"
            f"{spatial_pattern['water_relation']} 从传统风水文化表达看，水常被视为“财气流动”的象征；"
            "从现代地理解释看，应重点核验水体距离、洪水位、排水组织和建设退让要求。",
            "八、坡度坡向与采光分析\n"
            f"平均坡度 {terrain_metrics['mean_slope']} 度，最大坡度 {terrain_metrics['max_slope']} 度，"
            f"主要坡向为 {terrain_metrics['dominant_aspect']}。偏南、东南或西南坡向通常有较好的日照潜力，但需结合遮挡物复核。",
            "九、居住与建设建议\n" + "\n".join(f"{index + 1}. {item}" for index, item in enumerate(recommendations)),
            "十、民俗聚财格局娱乐解读\n"
            f"聚财格局文化参考分：{wealth_reference['wealth_culture_score']} 分。\n"
            f"{wealth_reference['tendency']}\n"
            "提升“纳气聚财”观感的环境整理：\n"
            + "\n".join(f"{index + 1}. {item}" for index, item in enumerate(wealth_reference["actions"]))
            + "\n注意：以上是民俗文化娱乐表达，不是财运预测，不可作为投资、经营、购房或商业决策依据。",
            "十一、建设适宜性与现代地理风险提示\n" + " ".join(risk_notes),
            "十二、综合评价\n"
            f"综合环境格局评分为 {scores['overall_score']} 分。该评分来自高程、坡度、坡向、围合度和水系占位等规则指标，"
            "用于 MVP 阶段的环境格局比较，不应用作单一决策依据。",
            "十三、免责声明\n" + DISCLAIMER,
        ]
    )
