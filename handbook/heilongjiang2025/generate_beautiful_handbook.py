#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
黑龙江旅游手册生成器 - 美观彩色版
基于提供的行程和图片素材，生成专业的PDF手册
"""

import os
import sys
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import HexColor, white, black, blue, darkblue, lightblue, green, darkgreen, orange, red
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import glob

class BeautifulHandbookGenerator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.materials_dir = os.path.join(self.base_dir, 'materials')
        self.details_dir = os.path.join(self.materials_dir, 'details')
        
        # 色彩主题 - 黑龙江元素
        self.colors = {
            'primary': HexColor('#2E5984'),      # 深蓝色 - 代表松花江
            'secondary': HexColor('#4A90A4'),    # 青蓝色 - 代表湖泊
            'accent': HexColor('#8FBC8F'),       # 森林绿
            'warm': HexColor('#D2691E'),         # 橙棕色 - 代表秋叶
            'light': HexColor('#F0F8FF'),        # 爱丽丝蓝 - 浅色背景
            'header': HexColor('#1E3A5F'),       # 深蓝标题色
            'text': HexColor('#2F2F2F'),         # 深灰文本色
        }
        
        self.setup_fonts()
        self.setup_styles()
        
    def setup_fonts(self):
        """设置字体"""
        # 尝试加载系统中文字体
        try:
            # Windows 系统字体路径
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
                "C:/Windows/Fonts/simsun.ttc",    # 宋体
                "C:/Windows/Fonts/simhei.ttf",    # 黑体
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        if font_path.endswith('.ttc'):
                            pdfmetrics.registerFont(TTFont('Chinese', font_path, subfontIndex=0))
                        else:
                            pdfmetrics.registerFont(TTFont('Chinese', font_path))
                        break
                    except Exception as e:
                        continue
            else:
                print("警告: 未找到中文字体，将使用默认字体")
                
        except Exception as e:
            print(f"字体加载异常: {e}")
    
    def setup_styles(self):
        """设置样式"""
        self.styles = getSampleStyleSheet()
        
        # 标题样式
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            spaceBefore=20,
            textColor=self.colors['header'],
            alignment=TA_CENTER,
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        ))
        
        # 章节标题样式
        self.styles.add(ParagraphStyle(
            name='ChapterTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            spaceBefore=15,
            textColor=self.colors['primary'],
            leftIndent=0,
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        ))
        
        # 子标题样式
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=10,
            textColor=self.colors['secondary'],
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        ))
        
        # 正文样式
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            spaceBefore=4,
            textColor=self.colors['text'],
            alignment=TA_JUSTIFY,
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        ))
        
        # 重点文本样式
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['CustomBodyText'],
            fontSize=12,
            textColor=self.colors['warm'],
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
        ))
    
    def create_cover_page(self, elements):
        """创建封面页"""
        # 封面标题
        title = Paragraph("2025 黑龙江深度探索之旅", self.styles['CustomTitle'])
        elements.append(Spacer(1, 1*inch))
        elements.append(title)
        elements.append(Spacer(1, 0.5*inch))
        
        # 副标题
        subtitle = Paragraph("小兴安岭森林 · 火山地质奇观 · 湿地生态体验", self.styles['SubTitle'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.8*inch))
        
        # 行程概览图
        overview_image = os.path.join(self.materials_dir, '行程总览图.png')
        if os.path.exists(overview_image):
            img = Image(overview_image, width=5*inch, height=3.5*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.5*inch))
        
        # 行程日期和信息
        info_data = [
            ['出行日期', '2025年8月16日 - 8月24日（9天8夜）'],
            ['行程亮点', '哈尔滨历史文化 · 扎龙丹顶鹤 · 五大连池火山'],
            ['', '黑河边境风情 · 小兴安岭森林 · 松花江风光'],
            ['交通方式', '高铁往返 + 自驾深度游'],
            ['适合人群', '家庭出游 · 自然爱好者 · 摄影发烧友']
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.colors['light']),
            ('TEXTCOLOR', (0, 0), (0, -1), self.colors['header']),
            ('TEXTCOLOR', (1, 0), (1, -1), self.colors['text']),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, self.colors['secondary']),
            ('BOX', (0, 0), (-1, -1), 1, self.colors['primary']),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, self.colors['light']]),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # 制作信息
        creation_date = datetime.now().strftime("%Y年%m月")
        footer_text = f"手册制作时间：{creation_date} | 专属定制旅行手册"
        footer = Paragraph(footer_text, self.styles['CustomBodyText'])
        elements.append(Spacer(1, 1*inch))
        elements.append(footer)
        
        elements.append(PageBreak())
    
    def create_overview_section(self, elements):
        """创建行程总览章节"""
        elements.append(Paragraph("📅 行程总览", self.styles['ChapterTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 行程总览表格
        overview_data = [
            ['天数', '日期', '目的地', '核心体验', '住宿地点'],
            ['Day 1', '8/16 (六)', '哈尔滨', '中央大街 + 松花江 + 中华巴洛克', '哈尔滨中央大街'],
            ['Day 2', '8/17 (日)', '哈尔滨', '太阳岛清凉绿地 + 东北虎林园', '哈尔滨中央大街'],
            ['Day 3', '8/18 (一)', '齐齐哈尔', '扎龙湿地观鹤生态', '齐齐哈尔'],
            ['Day 4', '8/19 (二)', '五大连池', '黑龙山火山徒步 + 北饮泉', '五大连池镇'],
            ['Day 5', '8/20 (三)', '黑河', '瑷珲陈列馆 + 江畔远眺俄罗斯', '黑河市区'],
            ['Day 6', '8/21 (四)', '嘉荫/茅兰沟', '峡谷溪流徒步', '嘉荫或伊春'],
            ['Day 7', '8/22 (五)', '汤旺河+五营', '花岗岩奇石 + 红松森林浴', '伊春'],
            ['Day 8', '8/23 (六)', '伊春→哈尔滨', '金山鹿苑 + 返哈夜生活', '哈尔滨西站'],
            ['Day 9', '8/24 (日)', '哈尔滨→北京', '高铁返程', '返程']
        ]
        
        overview_table = Table(overview_data, colWidths=[0.8*inch, 1.2*inch, 1.3*inch, 2.2*inch, 1.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, self.colors['secondary']),
            ('BOX', (0, 0), (-1, -1), 1, self.colors['primary']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light']]),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(overview_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # 交通安排表格
        elements.append(Paragraph("🚗 交通安排", self.styles['SubTitle']))
        
        transport_data = [
            ['路段', '交通方式', '预计时长', '关键时间点'],
            ['北京→哈尔滨', 'G901高铁', '4h33min', '08:00-12:33'],
            ['哈尔滨→齐齐哈尔', '自驾', '3.5-4h', '08:00出发'],
            ['齐齐哈尔→五大连池', '自驾', '4.5h', '09:00出发'],
            ['五大连池→黑河', '自驾', '3-3.5h', '09:00出发'],
            ['黑河→嘉荫茅兰沟', '自驾', '3h', '09:00出发'],
            ['伊春→哈尔滨', '自驾', '4.5-5h', '11:00出发'],
            ['哈尔滨→北京', 'G906高铁', '4h34min', '09:52-14:26']
        ]
        
        transport_table = Table(transport_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 2*inch])
        transport_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, self.colors['secondary']),
            ('BOX', (0, 0), (-1, -1), 1, self.colors['secondary']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light']]),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(transport_table)
        elements.append(PageBreak())
    
    def create_daily_itinerary(self, elements, day_num, title, description, highlights, map_files):
        """创建每日行程页面"""
        elements.append(Paragraph(f"Day {day_num}: {title}", self.styles['ChapterTitle']))
        elements.append(Spacer(1, 0.15*inch))
        
        # 当日概述
        elements.append(Paragraph("🎯 当日概述", self.styles['SubTitle']))
        desc_para = Paragraph(description, self.styles['CustomBodyText'])
        elements.append(desc_para)
        elements.append(Spacer(1, 0.15*inch))
        
        # 亮点体验
        elements.append(Paragraph("⭐ 亮点体验", self.styles['SubTitle']))
        for highlight in highlights:
            highlight_para = Paragraph(f"• {highlight}", self.styles['CustomBodyText'])
            elements.append(highlight_para)
        elements.append(Spacer(1, 0.2*inch))
        
        # 路线地图
        elements.append(Paragraph("🗺️ 路线地图", self.styles['SubTitle']))
        
        # 添加地图图片
        map_count = 0
        for map_file in map_files:
            map_path = os.path.join(self.details_dir, map_file)
            if os.path.exists(map_path):
                try:
                    img = Image(map_path, width=3*inch, height=2.5*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.1*inch))
                    map_count += 1
                    if map_count >= 2:  # 每页最多显示2张地图
                        break
                except Exception as e:
                    print(f"地图加载失败: {map_file}, 错误: {e}")
        
        elements.append(PageBreak())
    
    def create_destination_guides(self, elements):
        """创建目的地详细指南"""
        destinations = [
            {
                'name': '哈尔滨 - 北方巴黎',
                'description': '哈尔滨，被誉为"东方小巴黎"，是中国最具欧陆风情的城市之一。这里有着丰富的俄罗斯文化遗存，中央大街的巴洛克建筑群、圣索菲亚大教堂的拜占庭风格，都诉说着这座城市独特的历史。',
                'attractions': [
                    '中央大街 - 亚洲最长步行街，汇聚各国建筑风格',
                    '圣索菲亚大教堂 - 远东地区最大的东正教教堂',
                    '松花江风景区 - 母亲河畔的浪漫风光',
                    '太阳岛 - 避暑胜地和俄罗斯风情体验地',
                    '东北虎林园 - 世界最大的东北虎繁育基地'
                ],
                'tips': '最佳拍照时间是傍晚5-7点，中央大街的灯光开始亮起时最美。推荐品尝正宗的俄式西餐和马迭尔冰棍。'
            },
            {
                'name': '扎龙湿地 - 丹顶鹤的故乡',
                'description': '扎龙国家级自然保护区是世界最大的芦苇湿地，也是丹顶鹤的重要栖息和繁殖地。这里生活着世界上一半以上的野生丹顶鹤，是观鸟和生态摄影的天堂。',
                'attractions': [
                    '丹顶鹤放飞表演 - 每天四场，15:30是最后一场',
                    '湿地木栈道 - 2公里生态步道，深入芦苇荡',
                    '观鹤台 - 最佳观鸟和摄影位置',
                    '丹顶鹤博物馆 - 了解鹤类生态知识'
                ],
                'tips': '建议携带望远镜和长焦镜头。穿着浅色衣物，避免惊扰野生动物。最佳观鸟季节是春秋两季迁徙期。'
            },
            {
                'name': '五大连池 - 火山地质博物馆',
                'description': '五大连池是由火山熔岩阻塞白河河道形成的五个串珠状湖泊，被誉为"天然火山地质博物馆"。这里有世界保存最完整的火山地貌和珍贵的火山矿泉。',
                'attractions': [
                    '黑龙山 - 最高火山锥，可攀登到火山口',
                    '北饮泉 - 世界三大冷矿泉之一',
                    '五大连池湖区 - 火山堰塞湖群',
                    '地质博物馆 - 火山地质科普展示'
                ],
                'tips': '登山建议穿防滑鞋，火山石路面较滑。矿泉水可以直接饮用，但有特殊的铁锈味。'
            }
        ]
        
        elements.append(Paragraph("🏞️ 目的地深度解读", self.styles['ChapterTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        for dest in destinations:
            # 目的地名称
            elements.append(Paragraph(dest['name'], self.styles['SubTitle']))
            
            # 描述
            desc_para = Paragraph(dest['description'], self.styles['CustomBodyText'])
            elements.append(desc_para)
            elements.append(Spacer(1, 0.1*inch))
            
            # 主要景点
            elements.append(Paragraph("主要景点：", self.styles['Highlight']))
            for attraction in dest['attractions']:
                attr_para = Paragraph(f"• {attraction}", self.styles['CustomBodyText'])
                elements.append(attr_para)
            elements.append(Spacer(1, 0.1*inch))
            
            # 贴士
            tips_para = Paragraph(f"💡 游览贴士：{dest['tips']}", self.styles['Highlight'])
            elements.append(tips_para)
            elements.append(Spacer(1, 0.2*inch))
        
        elements.append(PageBreak())
    
    def create_practical_info(self, elements):
        """创建实用信息章节"""
        elements.append(Paragraph("🎒 实用信息", self.styles['ChapterTitle']))
        elements.append(Spacer(1, 0.2*inch))
        
        # 装备清单
        elements.append(Paragraph("必备装备清单", self.styles['SubTitle']))
        
        equipment_data = [
            ['类别', '物品', '用途说明'],
            ['证件文件', '身份证、驾照、行驶证', '住宿、景区、租车必需'],
            ['衣物装备', '速干长袖、轻薄外套、登山鞋', '适应温差和户外徒步'],
            ['防护用品', '防晒霜SPF50+、防蚊液', '强紫外线和湿地蚊虫防护'],
            ['摄影器材', '相机、长焦镜头、望远镜', '野生动物和风光摄影'],
            ['日用品', '保温杯、雨衣、登山杖', '户外活动舒适度提升']
        ]
        
        equipment_table = Table(equipment_data, colWidths=[1.5*inch, 2.5*inch, 3*inch])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['accent']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, self.colors['accent']),
            ('BOX', (0, 0), (-1, -1), 1, self.colors['accent']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light']]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(equipment_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # 美食推荐
        elements.append(Paragraph("🍜 特色美食推荐", self.styles['SubTitle']))
        
        food_recommendations = [
            "锅包肉 - 哈尔滨经典菜，外酥内嫩，酸甜可口",
            "红菜汤 - 俄式经典汤品，浓郁醇厚",
            "马迭尔冰棍 - 百年老店，哈尔滨必吃甜品",
            "东北乱炖 - 丰富食材的东北家常味道",
            "五大连池矿泉鱼 - 当地特色，肉质鲜美",
            "林区野生蘑菇 - 小兴安岭天然珍品"
        ]
        
        for food in food_recommendations:
            food_para = Paragraph(f"• {food}", self.styles['CustomBodyText'])
            elements.append(food_para)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # 摄影贴士
        elements.append(Paragraph("📸 摄影贴士", self.styles['SubTitle']))
        
        photo_tips = [
            "丹顶鹤拍摄：使用200mm以上长焦，快门速度1/500s以上",
            "建筑摄影：傍晚5-7点光线最佳，注意构图和透视",
            "风光摄影：携带三脚架，利用黄金时段光线",
            "人像拍摄：注意背景选择，突出当地特色元素",
            "设备保护：湿地和森林环境注意防潮防尘"
        ]
        
        for tip in photo_tips:
            tip_para = Paragraph(f"• {tip}", self.styles['CustomBodyText'])
            elements.append(tip_para)
        
        elements.append(Spacer(1, 0.3*inch))
        
        # 安全提醒
        elements.append(Paragraph("⚠️ 安全提醒", self.styles['SubTitle']))
        
        safety_tips = [
            "长途驾驶：每2小时休息一次，避免疲劳驾驶",
            "野生动物观赏：保持安全距离，不要投喂",
            "火山地貌徒步：穿防滑鞋，注意脚下安全",
            "湿地游览：注意防蚊虫叮咬，备好驱虫剂",
            "天气变化：随时关注天气预报，做好应对准备"
        ]
        
        for safety in safety_tips:
            safety_para = Paragraph(f"• {safety}", self.styles['CustomBodyText'])
            elements.append(safety_para)
    
    def generate_handbook(self):
        """生成手册"""
        # 创建输出文件名
        output_filename = os.path.join(self.base_dir, f"黑龙江深度探索手册_{datetime.now().strftime('%Y%m%d')}.pdf")
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        
        # 创建各个章节
        print("生成封面页...")
        self.create_cover_page(elements)
        
        print("生成行程总览...")
        self.create_overview_section(elements)
        
        # 每日详细行程
        daily_itineraries = [
            (1, "初探冰城哈尔滨", "抵达后游览中央大街、松花江风景区，感受欧陆风情", 
             ["中央大街建筑群", "圣索菲亚教堂", "防洪纪念塔", "松花江夜景"], 
             ["1-map-1.png", "1-map-2.png"]),
            
            (2, "太阳岛与虎林园", "上午太阳岛绿地休闲，下午东北虎林园观赏猛兽", 
             ["太阳岛风景区", "俄罗斯风情小镇", "东北虎林园", "江畔散步"], 
             ["2-map-1.png", "2-map-2.png"]),
            
            (3, "扎龙湿地观鹤", "前往齐齐哈尔扎龙湿地，观赏丹顶鹤放飞表演", 
             ["扎龙湿地保护区", "丹顶鹤放飞表演", "芦苇荡栈道", "湿地博物馆"], 
             ["3-map-1.png", "3-map-2.png"]),
            
            (4, "五大连池火山奇观", "黑龙山火山口徒步，北饮泉矿泉体验", 
             ["黑龙山火山锥", "火山口全景", "北饮泉矿泉", "地质博物馆"], 
             ["4-map-1.png", "4-map-2.png"]),
            
            (5, "黑河边境风情", "瑷珲历史文化，界江风光，边境夜市", 
             ["瑷珲历史陈列馆", "黑龙江公园", "中俄边境线", "边境夜市"], 
             ["5-map-1.png", "5-map-2.png"]),
            
            (6, "茅兰沟森林峡谷", "峡谷溪流徒步，原始森林体验", 
             ["茅兰沟国家森林公园", "峡谷栈道", "瀑布群", "森林氧吧"], 
             ["6-map-1.png", "6-map-2.png"]),
            
            (7, "小兴安岭深度游", "汤旺河奇石林，五营红松原始林", 
             ["汤旺河林海奇石", "花岗岩石林", "五营国家森林公园", "红松母树林"], 
             ["7-map-1.png", "7-map-2.png"]),
            
            (8, "返程哈尔滨", "金山鹿苑梅花鹿互动，返回哈尔滨", 
             ["金山鹿苑", "梅花鹿互动", "林区风光", "哈尔滨夜景"], 
             ["8-map-1.png", "8-map-2.png"])
        ]
        
        print("生成每日行程...")
        for day_info in daily_itineraries:
            self.create_daily_itinerary(elements, *day_info)
        
        print("生成目的地指南...")
        self.create_destination_guides(elements)
        
        print("生成实用信息...")
        self.create_practical_info(elements)
        
        # 生成PDF
        print(f"正在生成PDF文件: {output_filename}")
        doc.build(elements)
        
        print(f"✅ 手册生成完成！")
        print(f"📄 文件位置: {output_filename}")
        
        return output_filename

def main():
    try:
        generator = BeautifulHandbookGenerator()
        output_file = generator.generate_handbook()
        print(f"\n🎉 黑龙江旅游手册生成成功！")
        print(f"📁 文件路径: {output_file}")
        print(f"💡 现在您可以打印这份手册，开始您的黑龙江深度探索之旅！")
        
    except Exception as e:
        print(f"❌ 生成过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
