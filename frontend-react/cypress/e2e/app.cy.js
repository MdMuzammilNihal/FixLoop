describe('App E2E', () => {
  it('loads the app and shows the header and toolbar', () => {
    cy.visit('/');
    cy.get('header[role="banner"]').contains('FixLoop');
    cy.get('nav[aria-label="Toolbar"]');
    cy.get('select[aria-label="Select programming language"]');
  });
}); 