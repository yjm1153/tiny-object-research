from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "mentor_discussion" / "PRTiny_route_discussion_draft.pdf"


def register_fonts():
    regular = Path(r"C:\Windows\Fonts\Deng.ttf")
    bold = Path(r"C:\Windows\Fonts\Dengb.ttf")
    if not regular.exists():
        regular = Path(r"C:\Windows\Fonts\simhei.ttf")
    if not bold.exists():
        bold = regular
    pdfmetrics.registerFont(TTFont("DiscussionSans", str(regular)))
    pdfmetrics.registerFont(TTFont("DiscussionSans-Bold", str(bold)))


def P(text, style):
    return Paragraph(text, style)


def build_pdf():
    register_fonts()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    navy = colors.HexColor("#17324D")
    blue = colors.HexColor("#2F6690")
    light_blue = colors.HexColor("#EAF3F8")
    light_gray = colors.HexColor("#F3F5F7")
    orange = colors.HexColor("#B45F06")
    green = colors.HexColor("#2D6A4F")
    red = colors.HexColor("#9B2226")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCN", parent=styles["Title"], fontName="DiscussionSans-Bold",
        fontSize=22, leading=28, textColor=navy, alignment=TA_CENTER, spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        name="SubtitleCN", parent=styles["Normal"], fontName="DiscussionSans",
        fontSize=10.5, leading=16, textColor=colors.HexColor("#58636E"),
        alignment=TA_CENTER, spaceAfter=12,
    ))
    styles.add(ParagraphStyle(
        name="H1CN", parent=styles["Heading1"], fontName="DiscussionSans-Bold",
        fontSize=15, leading=21, textColor=navy, spaceBefore=8, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="H2CN", parent=styles["Heading2"], fontName="DiscussionSans-Bold",
        fontSize=11.5, leading=17, textColor=blue, spaceBefore=7, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="BodyCN", parent=styles["BodyText"], fontName="DiscussionSans",
        fontSize=9.4, leading=15, textColor=colors.HexColor("#27313A"),
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="SmallCN", parent=styles["BodyText"], fontName="DiscussionSans",
        fontSize=8.3, leading=12.5, textColor=colors.HexColor("#4B5560"),
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="CalloutCN", parent=styles["BodyText"], fontName="DiscussionSans",
        fontSize=10, leading=16, textColor=navy, leftIndent=2, rightIndent=2,
        spaceAfter=0,
    ))
    styles.add(ParagraphStyle(
        name="TableCN", parent=styles["BodyText"], fontName="DiscussionSans",
        fontSize=8.2, leading=11.5, textColor=colors.HexColor("#27313A"),
    ))
    styles.add(ParagraphStyle(
        name="TableHeadCN", parent=styles["BodyText"], fontName="DiscussionSans-Bold",
        fontSize=8.3, leading=11.5, textColor=colors.white,
    ))
    styles.add(ParagraphStyle(
        name="FooterCN", parent=styles["BodyText"], fontName="DiscussionSans",
        fontSize=7.5, leading=9, textColor=colors.HexColor("#6B7280"),
        alignment=TA_CENTER,
    ))

    doc = SimpleDocTemplate(
        str(OUT), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=14 * mm, bottomMargin=14 * mm, title="PRTiny 极小目标检测研究路线（导师讨论草案）",
        author="研究设计 agent",
    )

    story = []
    story.append(P("PRTiny 极小目标检测研究路线", styles["TitleCN"]))
    story.append(P("导师讨论草案｜2026-09-09｜非正式材料，不替代正式研究审查", styles["SubtitleCN"]))

    intro = [
        [P("这份材料想讨论什么", styles["TableHeadCN"]), P("目前研究已经证明了什么、还缺什么，以及是否值得继续投入。", styles["TableCN"])],
        [P("一句话判断", styles["TableHeadCN"]), P("路线仍有继续研究价值，也具备冲击 CCF-C 的方向基础；但现在还不是“可以直接写结论”的阶段。先把 PDD 实验中的基线异常和门禁矛盾解决，再决定是否进入完整方法。", styles["TableCN"])],
    ]
    t = Table(intro, colWidths=[35 * mm, 145 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), blue),
        ("BACKGROUND", (1, 0), (1, -1), light_blue),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B8CBD8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D8E2")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(P("1. 研究问题与基本想法", styles["H1CN"]))
    story.append(P("研究对象是有效尺寸约 2–8 像素的极小目标，主要关注漏检，而不是把所有小目标问题都混在一起。基本想法是：早期下采样容易丢掉极小目标的空间细节，因此先尝试保留浅层细节，再考虑是否需要轻量的可靠性增强。", styles["BodyCN"]))
    story.append(P("当前工作模型只有两个潜在实质改动：PDD（Partial Detail-Preserving Downsampling）和 SSR（Spatial–Spectral Reliable Refinement）。频率信息只作为“可靠性线索”，不能直接写成“高频等于极小目标”。", styles["BodyCN"]))

    story.append(P("2. 已经比较确定的证据", styles["H1CN"]))
    evidence = [
        [P("项目", styles["TableHeadCN"]), P("当前判断", styles["TableHeadCN"]), P("对论文的意义", styles["TableHeadCN"])],
        [P("P2 基线（PRT-001-A1）", styles["TableCN"]), P("已通过研究设计审查。相对 P3–P7，两个 seed 的平均 APvt 提升 +0.0103，平均 2–8 px ARvt 提升 +0.0131。", styles["TableCN"]), P("说明 P2 是合理的极小目标检测载体，但它本身不是方法创新。", styles["TableCN"])],
        [P("PDD v1 旧结果", styles["TableCN"]), P("零 AP 只能作为负测量线索。旧数据计数、冻结设置和实际拓扑存在不一致，不能直接解释为“PDD 失败”或“SSR 必要”。", styles["TableCN"]), P("需要受控诊断，避免把不公平对照写进论文。", styles["TableCN"])],
        [P("PDD-U 最新实验分支", styles["TableCN"]), P("实验 agent 报告 PDD-U 相对 B1-U 两个 seed 均为正，但 B1-U 两个 seed 的 AP/APvt/ARvt 全为 0；Gate B 与 seed2 灰区触发之间也有矛盾。该结果尚未经过研究设计终审。", styles["TableCN"]), P("暂时只能当作待审材料，不能作为因果结论。", styles["TableCN"])],
    ]
    t = Table(evidence, colWidths=[34 * mm, 92 * mm, 54 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), blue),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_gray]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B8CBD8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E0E6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    story.append(Spacer(1, 8))
    story.append(P("3. 当前最关键的讨论点", styles["H1CN"]))
    warning = Table([[P("先不要急着把 PDD-U 的正增益写成“PDD 必要性已证明”。基线 B1-U 两个 seed 全零是一个强异常：可能是训练/评估流程问题，也可能是全解冻基线本身没有学起来。若基线退化，PDD 的增益就不能被当作公平的因果比较。", styles["CalloutCN"])]], colWidths=[180 * mm])
    warning.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF4E5")),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#E6A23C")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(warning)
    story.append(Spacer(1, 7))
    for item in [
        "核对 B1-U 的训练日志、预测数量、loss、初始化、BN/optimizer 和评估脚本，确认“全零”是否真实。",
        "按任务卡重新检查 Gate B：平均 APvt 虽达到阈值，但平均 2–8 px ARvt 低于阈值，且已触发灰区 seed2 条件。",
        "在研究设计审查前，PDD-U 只能标为 READY_FOR_REVIEW；SSR、泛化和完整消融继续锁定。",
    ]:
        story.append(P("• " + item, styles["BodyCN"]))

    story.append(PageBreak())
    story.append(P("4. 建议的研究路线（按风险从低到高）", styles["H1CN"]))
    route = [
        [P("阶段", styles["TableHeadCN"]), P("要回答的问题", styles["TableHeadCN"]), P("交付物", styles["TableHeadCN"])],
        [P("A. 先收敛 PDD 诊断", styles["TableCN"]), P("B1-U 全零是否是流程异常？PDD-U 是否在公平基线上仍有稳定小幅收益？", styles["TableCN"]), P("修正后的审计、seed2（如触发）、正式结果审查；决定保留或删除 PDD。", styles["TableCN"])],
        [P("B. 冻结一个最小方法", styles["TableCN"]), P("如果 PDD 通过，是否值得加入 SSR？如果 PDD 不通过，是否改做更简单的空间细节模块？", styles["TableCN"]), P("PDD-only 或 PDD+SSR 的最小消融，不同时堆很多模块。", styles["TableCN"])],
        [P("C. 做能支撑论文的对照", styles["TableCN"]), P("收益来自模块本身，而不是参数量、训练策略或评估口径吗？", styles["TableCN"]), P("原模型、P2、空间-only、frequency-only、完整模型和必要控制；保持主指标一致。", styles["TableCN"])],
        [P("D. 做一次泛化验证", styles["TableCN"]), P("方法是否只在 AI-TOD-v2 有效？", styles["TableCN"]), P("至少一个第二数据集或第二检测器上的同方向证据；否则只做单数据集结论。", styles["TableCN"])],
        [P("E. 论文整理", styles["TableCN"]), P("能否用简单故事讲清楚问题、方法、证据和边界？", styles["TableCN"]), P("主表、消融表、可视化案例、失败案例、配置与复现实验说明。", styles["TableCN"])],
    ]
    t = Table(route, colWidths=[31 * mm, 76 * mm, 73 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), blue),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_gray]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B8CBD8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E0E6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    story.append(P("5. 论文定位的建议边界", styles["H1CN"]))
    for item in [
        "可以主张：面向 2–8 px 极小目标漏检，早期空间细节保留是一个值得验证的方向。",
        "暂时不能主张：PDD 已经被证明有效、SSR 必然必要、频率信息本身等于极小目标证据，或方法已经跨数据集泛化。",
        "如果最终只有 P2 基线稳定提升，建议把它定位为可靠基线与研究平台，不要把基线提升包装成新方法。",
        "如果 PDD 通过且 SSR 的增益超过容量匹配的空间-only 对照，才形成比较完整的 CCF-C 论文故事。",
    ]:
        story.append(P("• " + item, styles["BodyCN"]))

    story.append(Spacer(1, 5))
    story.append(P("6. 粗略时间安排（以结果不需要大幅返工为前提）", styles["H1CN"]))
    timeline = [
        [P("时间", styles["TableHeadCN"]), P("建议重点", styles["TableHeadCN"]), P("阶段目标", styles["TableHeadCN"])],
        [P("9 月上旬–9 月下旬", styles["TableCN"]), P("解决 B1-U 全零、核对 Gate B/seed2，完成 PDD 去留裁决。", styles["TableCN"]), P("方法路线冻结。", styles["TableCN"])],
        [P("10 月", styles["TableCN"]), P("完成最小消融与必要重跑，开始整理主表和失败案例。", styles["TableCN"]), P("得到可解释的核心结果。", styles["TableCN"])],
        [P("11 月", styles["TableCN"]), P("第二数据集或第二检测器验证；同步写方法、实验和讨论。", styles["TableCN"]), P("形成完整初稿。", styles["TableCN"])],
        [P("11 月下旬–12 月", styles["TableCN"]), P("内部修改、补图表、复核 Git 证据链并准备投稿。", styles["TableCN"]), P("具备 CCF-C 投稿条件；录用时间无法保证。", styles["TableCN"])],
    ]
    t = Table(timeline, colWidths=[39 * mm, 91 * mm, 50 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), green),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_gray]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B8CBD8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E0E6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)

    story.append(PageBreak())
    story.append(P("7. 和导师讨论时可以直接问的三个问题", styles["H1CN"]))
    questions = [
        "我们是否同意把“B1-U 全零”视为必须先解释的实验异常，而不是直接接受 PDD 的大幅相对增益？",
        "如果 PDD 在公平基线上只有小幅但稳定的提升，是否仍值得保留，并把贡献收缩为“极小目标空间细节保留”？",
        "论文目标是优先赶下一轮 CCF-C 投稿，还是先补更强的第二数据集/第二检测器证据以提高说服力？",
    ]
    for i, q in enumerate(questions, 1):
        box = Table([[P(f"{i}", styles["TableHeadCN"]), P(q, styles["CalloutCN"])]], colWidths=[13 * mm, 167 * mm])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), blue),
            ("BACKGROUND", (1, 0), (1, 0), light_blue),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#B8CBD8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8D8E2")),
            ("ALIGN", (0, 0), (0, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ]))
        story.append(box)
        story.append(Spacer(1, 8))

    story.append(P("8. 依据与说明", styles["H1CN"]))
    story.append(P("本草案只依据仓库当前版本化文件和远端可见实验分支整理。已审查证据主要来自 PRT-001-A1；PRT-002-A1 的最新结果分支尚未完成研究设计终审，因此文中对其采用“实验 agent 报告/待审”的表述。若本草案与后续正式审查记录冲突，以 AGENTS.md、decision、任务卡和正式研究审查为准。", styles["BodyCN"]))
    refs = [
        "docs/memory/CURRENT_STATE.md",
        "docs/research_brief_v0.1.md",
        "docs/decisions/DR-004-ccf-c-paced-evidence-standard.md",
        "research/reviews/2026-08-26-PRT-001-A1-result-review-3.md",
        "research/reviews/2026-08-26-PRT-002-A1-design-review-1.md",
        "experiment_handoffs/tasks/PRT-002-A1-pdd-causal-diagnostic.md",
        "origin/codex/exp-prt-002-a1:experiment_handoffs/results/PRT-002-A1-pdd-causal-diagnostic.md（待审）",
    ]
    story.append(P("参考文件：" + "；".join(refs), styles["SmallCN"]))
    story.append(Spacer(1, 8))
    story.append(P("讨论版结论：路线值得继续，但下一步不是继续堆模块，而是先把 PDD 诊断做成可信的、可解释的结果。", styles["CalloutCN"]))

    def footer(canvas, doc_obj):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D7E0E6"))
        canvas.line(16 * mm, 10 * mm, 194 * mm, 10 * mm)
        canvas.setFont("DiscussionSans", 7.5)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawCentredString(105 * mm, 6 * mm, f"PRTiny 研究路线讨论草案 · 第 {doc_obj.page} 页")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return OUT


if __name__ == "__main__":
    print(build_pdf())
