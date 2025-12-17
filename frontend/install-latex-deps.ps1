# Install dependencies for LaTeX rendering in Markdown
Write-Host "Installing LaTeX rendering dependencies..." -ForegroundColor Green

cd frontend

npm install remark-math rehype-katex katex

Write-Host "`nDependencies installed successfully!" -ForegroundColor Green
Write-Host "You can now use LaTeX expressions in Markdown descriptions." -ForegroundColor Cyan
Write-Host "  - Inline math: `$x^2 + y^2 = z^2`$" -ForegroundColor Yellow
Write-Host "  - Display math: `$`$\int_0^\infty e^{-x^2} dx`$`$" -ForegroundColor Yellow
