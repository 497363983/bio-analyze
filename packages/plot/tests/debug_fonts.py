import matplotlib.pyplot as plt
from matplotlib import font_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_fonts():
    # 获取所有可用字体的名称
    font_names = sorted([f.name for f in font_manager.fontManager.ttflist])
    
    logger.info("Checking for Chinese fonts...")
    target_fonts = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "SimSun"]
    found_fonts = []
    for font in target_fonts:
        if font in font_names:
            logger.info(f"Found font: {font}")
            found_fonts.append(font)
        else:
            logger.info(f"Font not found: {font}")
            
    # 打印当前的 rcParams
    logger.info(f"Current font.sans-serif: {plt.rcParams['font.sans-serif']}")
    
    # 尝试设置字体并绘图
    if found_fonts:
        plt.rcParams['font.sans-serif'] = found_fonts + plt.rcParams['font.sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, ax = plt.subplots()
        ax.set_title("中文标题测试")
        ax.text(0.5, 0.5, "中文文本", ha='center')
        try:
            fig.savefig("test_font_check.png")
            logger.info("Successfully saved test plot.")
        except Exception as e:
            logger.error(f"Failed to save plot: {e}")
    else:
        logger.warning("No common Chinese fonts found on this system.")

if __name__ == "__main__":
    check_fonts()
