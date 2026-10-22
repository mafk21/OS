# Pre-Commit & Pull Request Checklist

1. **Zero secrets**: Confirm no API keys, `.env` files, OAuth tokens, or private certs appear in `git status` or `git diff`.
2. **Tests green**: Confirm new behavior has test coverage and the test suite passes.
3. **Clean working tree**: Remove temporary debug prints, scratch files, or test artifacts before staging.
4. **Clear commit & PR summary**: State *what* changed, *why*, and *how it was verified* in concise engineering prose.
