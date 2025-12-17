# 🚀 Quick Start: Using LaTeX in Assignments

## For Teachers

### Creating an Assignment with Math

1. **Go to Teacher Dashboard**
   - Navigate to your teacher dashboard
   - Click "Create Assignment"

2. **Write Description with LaTeX**
   ```markdown
   # Python Functions - Circle Area
   
   Write a function to calculate the area of a circle.
   
   The formula is: $A = \pi r^2$
   
   Where:
   - $A$ is the area
   - $r$ is the radius
   - $\pi \approx 3.14159$
   ```

3. **Preview Your Work**
   - Click the "Preview" tab
   - See your math rendered professionally
   - Switch back to "Edit" to make changes

4. **Add Questions with Math**
   - Click "Add Question"
   - Write question description with LaTeX
   - Use the Preview tab for each question
   - Example:
     ```markdown
     Calculate the derivative of $f(x) = x^2 + 3x$
     
     Hint: Use the power rule: $\frac{d}{dx}[x^n] = nx^{n-1}$
     ```

5. **Use the Reference Guide**
   - Click "LaTeX Math Reference" in the form
   - Copy syntax examples
   - See common symbols and patterns

### Common LaTeX Patterns

```markdown
# Inline Math (in a sentence)
The quadratic formula is $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$

# Display Math (centered on its own line)
$$\int_0^1 x^2 dx = \frac{1}{3}$$

# Greek Letters
$\alpha$, $\beta$, $\gamma$, $\pi$, $\theta$

# Fractions
$\frac{a}{b}$ or $\frac{numerator}{denominator}$

# Exponents and Subscripts
$x^2$, $x^{2n+1}$, $x_i$, $x_{i,j}$

# Calculus
- Derivative: $\frac{dy}{dx}$
- Integral: $\int_a^b f(x) dx$
- Limit: $\lim_{x \to 0} \frac{\sin(x)}{x}$
- Summation: $\sum_{i=1}^{n} x_i$

# Comparison Operators
$\leq$, $\geq$, $\neq$, $\approx$

# Special Symbols
$\infty$, $\pm$, $\times$, $\div$
```

### Tips

1. **Always preview** before creating - catch any syntax errors
2. **Use inline math** ($...$) for formulas in sentences
3. **Use display math** ($$...$$) for important equations
4. **Check the reference guide** if you forget syntax
5. **Visit /latex-demo** for comprehensive examples

## For Students

No special action needed! When you view assignments:
- Math expressions render automatically
- Everything looks professional
- Focus on solving the problems

## Examples

### Example 1: Basic Algebra
```markdown
Solve for $x$ in the equation $2x + 5 = 15$
```

### Example 2: Calculus
```markdown
Find the area under the curve:
$$A = \int_0^2 (x^2 + 1) dx$$
```

### Example 3: Statistics
```markdown
The mean is calculated as:
$$\mu = \frac{1}{n} \sum_{i=1}^{n} x_i$$
```

### Example 4: Linear Algebra
```markdown
Multiply the matrices:
$$\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix} \times \begin{pmatrix} 5 \\ 6 \end{pmatrix}$$
```

## Need Help?

- **Built-in reference**: Click "LaTeX Math Reference" in the form
- **Full examples**: Visit `/latex-demo` route
- **Documentation**: Check `DESCRIPTION_VIEWER.md`

---

**You're all set!** Start creating mathematical content in your assignments. 🎓✨
