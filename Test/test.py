import numpy as np
from scipy import stats

# Data points
X = np.array([350, 380, 346, 362, 421, 380, 466]) #实际距离
Y = np.array([385, 289, 358, 358, 344, 496, 389]) #识别距离
                        #准  #准
# Linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(X, Y)

print(f"Linear relationship: Y = {slope:.2f}X + {intercept:.2f}")
print(f"R² = {r_value**2:.3f}")

# Alternative: polynomial fit
coeffs = np.polyfit(X, Y, 2)
print(f"\nQuadratic: Y = {coeffs[0]:.4f}X² + {coeffs[1]:.2f}X + {coeffs[2]:.2f}")

"""

"""