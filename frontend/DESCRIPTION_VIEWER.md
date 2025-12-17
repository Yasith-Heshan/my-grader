# Description Viewer Component

## Overview
The `DescriptionViewer` component renders Markdown content with full LaTeX math support, perfect for displaying assignment descriptions, question descriptions, and other educational content with mathematical expressions.

## Features
- ✅ Full Markdown support
- ✅ Inline LaTeX math: `$x^2 + y^2 = z^2$`
- ✅ Display LaTeX math: `$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$`
- ✅ Ant Design Typography integration
- ✅ Code syntax highlighting
- ✅ Custom styling support

## Installation

Run the installation script to add required dependencies:

```powershell
.\frontend\install-latex-deps.ps1
```

Or manually install:

```bash
cd frontend
npm install remark-math rehype-katex katex
```

## Usage

### Basic Usage

```tsx
import DescriptionViewer from './components/DescriptionViewer';

function AssignmentView() {
  const description = `
# Python Functions Assignment

Write a function to calculate the **area of a circle** with radius $r$.

The formula is: $$A = \pi r^2$$

## Requirements
- Use $\pi \approx 3.14159$
- Return the result rounded to 2 decimal places
`;

  return <DescriptionViewer content={description} />;
}
```

### With Custom Styling

```tsx
<DescriptionViewer
  content={description}
  style={{ padding: '16px', backgroundColor: '#fafafa' }}
  className="assignment-description"
/>
```

## LaTeX Examples

### Inline Math
```markdown
The quadratic formula is $x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$
```

### Display Math
```markdown
Euler's identity:
$$e^{i\pi} + 1 = 0$$
```

### Complex Expressions
```markdown
The Fourier Transform:
$$\hat{f}(\xi) = \int_{-\infty}^{\infty} f(x) e^{-2\pi i x \xi} dx$$
```

## Integration with Existing Components

### In Assignment Form (Preview)
```tsx
import DescriptionViewer from './DescriptionViewer';

// In your AssignmentForm component, add a preview section:
<Form.Item label="Description Preview">
  <DescriptionViewer content={form.getFieldValue('description') || ''} />
</Form.Item>
```

### In Assignment Display
```tsx
import DescriptionViewer from './DescriptionViewer';

function AssignmentDetail({ assignment }) {
  return (
    <Card title={assignment.title}>
      <DescriptionViewer content={assignment.description} />
      {/* Rest of assignment content */}
    </Card>
  );
}
```

### In Question Display
```tsx
import DescriptionViewer from './DescriptionViewer';

function QuestionCard({ question }) {
  return (
    <Card title={`Question ${question.question_number}`}>
      <DescriptionViewer content={question.description} />
      {/* Code editor and other question content */}
    </Card>
  );
}
```

## Supported Markdown Features

- **Headers**: `# H1`, `## H2`, etc.
- **Bold**: `**bold text**`
- **Italic**: `*italic text*`
- **Lists**: Unordered (`-`, `*`) and ordered (`1.`, `2.`)
- **Links**: `[text](url)`
- **Code blocks**: Triple backticks
- **Inline code**: Single backticks
- **Blockquotes**: `>`

## LaTeX Reference

### Common Symbols
- Fractions: `\frac{numerator}{denominator}`
- Square root: `\sqrt{x}` or `\sqrt[n]{x}`
- Exponents: `x^2` or `x^{2n+1}`
- Subscripts: `x_1` or `x_{i,j}`
- Greek letters: `\alpha`, `\beta`, `\gamma`, `\pi`, etc.

### Common Operations
- Sum: `\sum_{i=1}^{n}`
- Integral: `\int_a^b`
- Product: `\prod_{i=1}^{n}`
- Limit: `\lim_{x \to \infty}`

### Matrices
```latex
$$
\begin{pmatrix}
a & b \\
c & d
\end{pmatrix}
$$
```

## Notes

- The component automatically includes KaTeX CSS for proper math rendering
- LaTeX expressions must be wrapped in `$` (inline) or `$$` (display)
- For complex expressions, prefer display math mode for better readability
