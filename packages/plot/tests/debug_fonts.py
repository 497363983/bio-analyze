from matplotlib.font_manager import fontManager
import matplotlib.pyplot as plt

print("Available fonts:")
# sorted_fonts = sorted([f.name for f in fontManager.ttflist])
# for font in sorted_fonts:
#     print(font)

# Check specifically for Chinese fonts
chinese_fonts = ["SimHei", "Microsoft YaHei", "SimSun", "Arial Unicode MS", "PingFang SC"]
print("\nChecking for common Chinese fonts:")
found_fonts = []
for font_name in chinese_fonts:
    try:
        # Try to find the font
        font = fontManager.findfont(font_name, fallback_to_default=False)
        print(f"  [FOUND] {font_name} -> {font}")
        found_fonts.append(font_name)
    except ValueError:
        print(f"  [MISSING] {font_name}")

print(f"\nFound Chinese fonts: {found_fonts}")

# Test plotting
if found_fonts:
    plt.rcParams['font.sans-serif'] = found_fonts
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    ax.set_title("??????")
    ax.set_xlabel("X?")
    ax.set_ylabel("Y?")
    
    try:
        fig.savefig("test_font_debug.png")
        print("\nSaved test_font_debug.png")
    except Exception as e:
        print(f"\nFailed to save plot: {e}")
else:
    print("\nNo Chinese fonts found, skipping plot test.")
