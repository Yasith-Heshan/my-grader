import React from 'react';
import { Card, Space, Typography, Divider } from 'antd';
import DescriptionViewer from '../components/DescriptionViewer';

const { Title, Paragraph } = Typography;

/**
 * Demo page showing LaTeX rendering capabilities
 */
const LatexDemo: React.FC = () => {
    const exampleContent1 = `
# Python Functions Assignment

## Overview
Write a function to calculate the **area of a circle** with radius $r$.

## Formula
The area of a circle is given by the formula:

$$A = \\pi r^2$$

where:
- $A$ is the area
- $r$ is the radius
- $\\pi \\approx 3.14159$

## Requirements
1. Function should accept radius as parameter
2. Return result rounded to 2 decimal places
3. Handle edge case when $r \\leq 0$
`;

    const exampleContent2 = `
# Quadratic Equation Solver

Solve the quadratic equation $ax^2 + bx + c = 0$ using the quadratic formula:

$$x = \\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}$$

## Test Cases
- For $a=1, b=-5, c=6$: Solutions are $x=2$ and $x=3$
- For $a=1, b=0, c=-4$: Solutions are $x=\\pm 2$
`;

    const exampleContent3 = `
# Calculus Problem

## Part A: Differentiation
Find the derivative of $f(x) = x^3 + 2x^2 - 5x + 1$

The power rule states: $\\frac{d}{dx}[x^n] = nx^{n-1}$

## Part B: Integration
Evaluate the definite integral:

$$\\int_0^1 (3x^2 + 2x) dx$$

## Part C: Limits
Calculate the limit:

$$\\lim_{x \\to 0} \\frac{\\sin(x)}{x} = 1$$
`;

    const exampleContent4 = `
# Matrix Operations

## Matrix Multiplication
Given matrices:

$$A = \\begin{pmatrix} 1 & 2 \\\\ 3 & 4 \\end{pmatrix}, \\quad B = \\begin{pmatrix} 5 & 6 \\\\ 7 & 8 \\end{pmatrix}$$

Calculate $C = AB$

## Determinant
The determinant of a $2 \\times 2$ matrix is:

$$\\det(A) = \\begin{vmatrix} a & b \\\\ c & d \\end{vmatrix} = ad - bc$$
`;

    return (
        <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
            <Title level={2}>LaTeX Rendering Examples</Title>
            <Paragraph>
                These examples demonstrate how LaTeX expressions render in assignment descriptions.
                Teachers can use inline math (with $...$) and display math (with $$...$$) to create
                professional mathematical content.
            </Paragraph>

            <Divider />

            <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <Card title="Example 1: Basic Math Formula">
                    <DescriptionViewer content={exampleContent1} />
                </Card>

                <Card title="Example 2: Quadratic Formula">
                    <DescriptionViewer content={exampleContent2} />
                </Card>

                <Card title="Example 3: Calculus">
                    <DescriptionViewer content={exampleContent3} />
                </Card>

                <Card title="Example 4: Linear Algebra">
                    <DescriptionViewer content={exampleContent4} />
                </Card>

                <Card title="LaTeX Syntax Reference">
                    <Typography>
                        <Title level={5}>Inline Math</Title>
                        <Paragraph>
                            Use single dollar signs: <code>$x^2 + y^2 = z^2$</code> renders as:{' '}
                            <DescriptionViewer content="$x^2 + y^2 = z^2$" />
                        </Paragraph>

                        <Title level={5}>Display Math</Title>
                        <Paragraph>
                            Use double dollar signs: <code>$$\int_0^\infty e^{`{-x^2}`} dx$$</code> renders as:
                            <DescriptionViewer content="$$\\int_0^\\infty e^{-x^2} dx$$" />
                        </Paragraph>

                        <Title level={5}>Common Symbols</Title>
                        <ul>
                            <li>Greek letters: <code>\alpha, \beta, \gamma, \pi</code></li>
                            <li>Fractions: <code>\frac{`{numerator}{denominator}`}</code></li>
                            <li>Square root: <code>\sqrt{`{x}`}</code> or <code>\sqrt[n]{`{x}`}</code></li>
                            <li>Summation: <code>\sum_{`{i=1}^{n}`}</code></li>
                            <li>Integral: <code>\int_a^b</code></li>
                            <li>Limit: <code>\lim_{`{x \to \infty}`}</code></li>
                        </ul>
                    </Typography>
                </Card>
            </Space>
        </div>
    );
};

export default LatexDemo;
