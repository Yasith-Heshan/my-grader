# 🧪 Manual Testing Guide for LaTeX Integration

## Quick Test Samples

Use these ready-to-paste samples to test LaTeX rendering in your assignment form.

---

## Test 1: Basic Math (Quick Test)

### Assignment Title:
```
Circle Area Calculator
```

### Assignment Description:
```markdown
# Calculate Circle Area

Write a function to calculate the area of a circle with radius $r$.

The formula is: $A = \pi r^2$

Where:
- $A$ is the area
- $r$ is the radius
- $\pi \approx 3.14159$
```

### Question 1:
**Title:** `Calculate Area`
**Description:**
```markdown
Implement the function using $A = \pi r^2$

Return result rounded to 2 decimal places.
```
**Points:** `10`

---

## Test 2: Calculus Expressions

### Assignment Description:
```markdown
# Derivatives and Integrals

## Derivative
The derivative of $f(x)$ is:
$$f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$$

## Integral
The definite integral:
$$\int_a^b f(x) dx$$

## Power Rule
$$\frac{d}{dx}[x^n] = nx^{n-1}$$
```

---

## Test 3: Complex Math (Comprehensive)

### Assignment Description:
```markdown
# Advanced Mathematics

## Quadratic Formula
$$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$

## Greek Letters
- Alpha: $\alpha$
- Beta: $\beta$  
- Gamma: $\gamma$
- Pi: $\pi$
- Theta: $\theta$
- Sigma: $\sigma$

## Matrix Example
$$\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}$$

## Summation
$$\sum_{i=1}^{n} x_i = x_1 + x_2 + ... + x_n$$
```

---

## Test 4: Statistics

### Assignment Description:
```markdown
# Statistical Measures

## Mean
$$\mu = \frac{1}{n} \sum_{i=1}^{n} x_i$$

## Variance
$$\sigma^2 = \frac{1}{n} \sum_{i=1}^{n} (x_i - \mu)^2$$

## Standard Deviation
$$\sigma = \sqrt{\sigma^2}$$
```

---

## Testing Checklist

### ✅ Teacher Dashboard - Create Assignment

1. **Navigate** to Teacher Dashboard
2. **Click** "Create Assignment" button
3. **Paste** Test 1 data into the form

### ✅ Description Preview

4. **Type** some LaTeX in the description field
5. **Click** "Preview" tab
6. **Verify** math renders correctly
7. **Switch back** to "Edit" tab
8. **Make changes** and preview again

### ✅ LaTeX Reference Guide

9. **Click** "LaTeX Math Reference" 
10. **Expand** the collapsible section
11. **Browse** the examples
12. **Copy** some syntax

### ✅ Add Questions

13. **Click** "Add Question"
14. **Enter** question title
15. **Paste** Test 1 Question 1 description
16. **Click** Preview tab for question
17. **Verify** math renders in question

### ✅ Multiple Questions

18. **Add** 2-3 more questions
19. **Test** moving questions up/down
20. **Test** delete question
21. **Verify** question numbers update

### ✅ Create Assignment

22. **Fill** due date
23. **Click** "Create Assignment"
24. **Wait** for success message

### ✅ Student View - Assignment Detail

25. **Navigate** to Student Dashboard
26. **Click** on the assignment
27. **Verify** description renders with LaTeX
28. **Check** all math symbols display correctly

### ✅ Student View - Notebook

29. **Click** "View Details" or notebook view
30. **Verify** assignment description renders
31. **Scroll** through questions
32. **Check** each question description renders LaTeX
33. **Verify** inline math ($...$) renders inline
34. **Verify** display math ($$...$$) is centered

### ✅ Demo Page

35. **Navigate** to `/latex-demo` route
36. **Review** all examples
37. **Verify** all math renders correctly
38. **Check** reference section

---

## What to Look For

### ✅ Correct Rendering:
- Math expressions appear professionally typeset
- Fractions stack properly: $\frac{a}{b}$
- Greek letters display: α, β, π
- Square roots have proper radicals: √
- Subscripts are lower: $x_i$
- Superscripts are raised: $x^2$

### ❌ Issues to Watch For:
- Raw LaTeX code visible (e.g., `\frac{a}{b}`)
- Dollar signs showing: `$x^2$` instead of rendered x²
- Math not centered in display mode
- Preview not updating when editing

---

## Sample Data File

Use the included `sample-latex-assignments.json` file for comprehensive testing:

1. Contains 6 complete assignments
2. Various math topics (geometry, calculus, linear algebra, statistics, physics, algebra)
3. Multiple questions per assignment
4. Different LaTeX complexity levels

**Note:** This JSON can be used as reference. Copy-paste individual sections into your form to test.

---

## Quick Copy-Paste Snippets

### Inline Math:
```
The area is $A = \pi r^2$ where $r$ is the radius.
```

### Display Math:
```
The quadratic formula:
$$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$$
```

### Greek Letters:
```
$\alpha$, $\beta$, $\gamma$, $\pi$, $\theta$, $\omega$, $\mu$, $\sigma$
```

### Fractions:
```
$\frac{1}{2}$, $\frac{a+b}{c+d}$, $\frac{numerator}{denominator}$
```

### Calculus:
```
$\frac{dy}{dx}$, $\int_a^b f(x) dx$, $\lim_{x \to 0}$, $\sum_{i=1}^{n}$
```

### Matrix:
```
$$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$$
```

---

## Expected Results

After testing, you should see:
- ✅ All math expressions render beautifully
- ✅ Preview matches final display
- ✅ Both teachers and students see proper formatting
- ✅ No LaTeX source code visible to end users
- ✅ Professional mathematical typesetting throughout

---

## Troubleshooting

**Issue:** LaTeX not rendering
- **Check:** Browser console for errors
- **Check:** Dependencies installed (`katex`, `remark-math`, `rehype-katex`)
- **Try:** Refresh the page

**Issue:** Preview not updating
- **Check:** You're typing in the Edit tab
- **Try:** Switch to Preview tab after making changes

**Issue:** Math displays as plain text
- **Check:** Using correct delimiters ($...$ or $$...$$)
- **Check:** No escaping issues with backslashes

---

Happy Testing! 🎓✨
