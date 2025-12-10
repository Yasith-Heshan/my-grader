import React from 'react';
import { Card, Typography, Button } from 'antd';

const { Title, Paragraph } = Typography;

interface State {
  hasError: boolean;
  error?: Error | null;
}

class ErrorBoundary extends React.Component<React.PropsWithChildren<{}>, State> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: any) {
    // eslint-disable-next-line no-console
    console.error('Uncaught error:', error, info);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24 }}>
          <Card>
            <Title level={3}>Something went wrong</Title>
            <Paragraph>
              The application encountered an error. Open the browser console for details.
            </Paragraph>
            <Paragraph type="secondary">{this.state.error?.message}</Paragraph>
            <Button type="primary" onClick={this.handleReload}>Reload</Button>
          </Card>
        </div>
      );
    }

    return this.props.children as React.ReactElement;
  }
}

export default ErrorBoundary;
