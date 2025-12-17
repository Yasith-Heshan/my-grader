import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { Typography } from 'antd';

const { Paragraph } = Typography;

interface DescriptionViewerProps {
  content: string;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Component to render Markdown content with LaTeX math support
 * - Inline math: $x^2 + y^2 = z^2$
 * - Display math: $$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$
 */
const DescriptionViewer: React.FC<DescriptionViewerProps> = ({
  content,
  className,
  style,
}) => {
  return (
    <div className={className} style={style}>
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // Customize rendering for better integration with Ant Design
          p: ({ children }) => <Paragraph>{children}</Paragraph>,
          h1: ({ children }) => <Typography.Title level={1}>{children}</Typography.Title>,
          h2: ({ children }) => <Typography.Title level={2}>{children}</Typography.Title>,
          h3: ({ children }) => <Typography.Title level={3}>{children}</Typography.Title>,
          h4: ({ children }) => <Typography.Title level={4}>{children}</Typography.Title>,
          h5: ({ children }) => <Typography.Title level={5}>{children}</Typography.Title>,
          code: ({ inline, children, ...props }: any) => {
            return inline ? (
              <code
                style={{
                  backgroundColor: '#f5f5f5',
                  padding: '2px 6px',
                  borderRadius: '3px',
                  fontFamily: 'monospace',
                }}
                {...props}
              >
                {children}
              </code>
            ) : (
              <pre
                style={{
                  backgroundColor: '#f5f5f5',
                  padding: '12px',
                  borderRadius: '4px',
                  overflow: 'auto',
                }}
              >
                <code {...props}>{children}</code>
              </pre>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default DescriptionViewer;
