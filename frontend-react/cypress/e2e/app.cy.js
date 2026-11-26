describe('App E2E', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('loads the app and shows the header and toolbar', () => {
    cy.get('header').contains('FixLoop');
    cy.get('nav[aria-label="Toolbar"]');
    cy.get('select[aria-label="Select programming language"]');
  });

  it('runs the code through /api/code when Execute is clicked', () => {
    cy.intercept('POST', '/api/code', (req) => {
      expect(req.body.action).to.eq('execute');
      req.reply({ execution_result: { stdout: 'Hello, World!\n', stderr: '' } });
    }).as('execute');
    cy.get('button[aria-label="Execute code"]').click();
    cy.wait('@execute');
    cy.get('.xterm-rows').should('contain.text', 'Hello, World!');
  });

  it('shows the input box when Input is ticked', () => {
    cy.get('textarea[aria-label="Execution Inputs"]').should('not.exist');
    cy.get('input[aria-label="Show input section"]').check({ force: true });
    cy.get('textarea[aria-label="Execution Inputs"]').should('exist');
  });

  it('shows backend errors in the Errors tab', () => {
    cy.intercept('POST', '/api/code', { statusCode: 503, body: { error: 'Ollama service is not available.' } });
    cy.get('button[aria-label="Analyze code"]').click();
    cy.contains('button', 'Errors').click();
    cy.contains('Ollama service is not available.');
  });
});
