import React from 'react';
import { Card, Typography, Space, Divider, Collapse } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';

const { Text, Paragraph } = Typography;
const { Panel } = Collapse;

/**
 * Quick reference guide for LaTeX math syntax
 * Can be displayed as a tooltip or help panel in the assignment form
 */
const LatexQuickReference: React.FC = () => {
    return (
        <Card
            size="small"
            title={
                <Space>
                    <InfoCircleOutlined />
                    <span>LaTeX Math Quick Reference</span>
                </Space>
            }
        >
            <Collapse ghost>
                <Panel header="Basic Syntax" key="1">
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div>
                            <Text strong>Inline math:</Text> <Text code>$x^2 + y^2 = z^2$</Text>
                        </div>
                        <div>
                            <Text strong>Display math:</Text> <Text code>$$\int_0^1 x dx$$</Text>
                        </div>
                    </Space>
                </Panel>

                <Panel header="Common Symbols" key="2">
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div><Text code>\alpha, \beta, \gamma</Text> → α, β, γ</div>
                        <div><Text code>\pi, \theta, \omega</Text> → π, θ, ω</div>
                        <div><Text code>\leq, \geq, \neq</Text> → ≤, ≥, ≠</div>
                        <div><Text code>\times, \div, \pm</Text> → ×, ÷, ±</div>
                        <div><Text code>\infty, \partial, \nabla</Text> → ∞, ∂, ∇</div>
                    </Space>
                </Panel>

                <Panel header="Fractions & Roots" key="3">
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div><Text code>\frac{`{a}{b}`}</Text> → fraction</div>
                        <div><Text code>\sqrt{`{x}`}</Text> → square root</div>
                        <div><Text code>\sqrt[n]{`{x}`}</Text> → nth root</div>
                    </Space>
                </Panel>

                <Panel header="Calculus" key="4">
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div><Text code>\int_a^b</Text> → integral</div>
                        <div><Text code>\sum_{`{i=1}^{n}`}</Text> → summation</div>
                        <div><Text code>\prod_{`{i=1}^{n}`}</Text> → product</div>
                        <div><Text code>\lim_{`{x \to 0}`}</Text> → limit</div>
                        <div><Text code>\frac{`{dy}{dx}`}</Text> → derivative</div>
                    </Space>
                </Panel>

                <Panel header="Subscripts & Superscripts" key="5">
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <div><Text code>x^2</Text> → superscript</div>
                        <div><Text code>x_i</Text> → subscript</div>
                        <div><Text code>x^{`{2n+1}`}</Text> → multi-char superscript</div>
                        <div><Text code>x_{`{i,j}`}</Text> → multi-char subscript</div>
                    </Space>
                </Panel>

                <Panel header="Matrices" key="6">
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        <Paragraph>
                            <pre style={{ fontSize: '11px' }}>{`$$\\begin{pmatrix}
a & b \\\\
c & d
\\end{pmatrix}$$`}</pre>
                        </Paragraph>
                    </Space>
                </Panel>

                <Panel header="Example Assignment Description" key="7">
                    <Paragraph>
                        <pre style={{ fontSize: '11px' }}>{`# Calculate Circle Area

Write a function that takes radius $r$ as input.

The formula is: $$A = \\pi r^2$$

where $A$ is the area and $r$ is the radius.`}</pre>
                    </Paragraph>
                </Panel>
            </Collapse>

            <Divider style={{ margin: '12px 0' }} />

            <Space direction="vertical" size={4}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                    💡 Use single $ for inline math: <Text code>$x^2$</Text>
                </Text>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                    💡 Use double $$ for display math: <Text code>$$\int x dx$$</Text>
                </Text>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                    📚 <a href="/latex-demo" target="_blank">View full examples →</a>
                </Text>
            </Space>
        </Card>
    );
};

export default LatexQuickReference;
