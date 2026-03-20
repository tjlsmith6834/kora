export const SHADOW_CSS_STRING = `
  /* ====================== */
  /*       Fonts            */
  /* ====================== */

  @import url("https://fonts.googleapis.com/css2?family=Lexend:wght@400;500;600&display=swap");
  @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap");
  @import url("https://fonts.googleapis.com/css2?family=Space+Grotesque:wght@400;500;600&display=swap");
  @import url("https://fonts.googleapis.com/css2?family=Spectral:wght@400;500&family=Varela+Round&display=swap");

  /* ====================== */
  /*   Host + Design Tokens */
  /* ====================== */

  :host {
    display: block;

    /*======================*/
    /*         Colors       */
    /*======================*/

    /* ###Text */
    --color-h1: black;
    --color-h2: #4A4A4A;
    --color-h3: #4A4A4A;
    --color-body: #5A5A5A;
    --color-user-input: #5A5A5A;

    /* ###Buttons */
    --color-postive-base: #BB4DFF;
    --color-positive-hover: #993ACC;
    --color-postive-text: #ffffff;

    --color-negative-base: #ffffff;
    --color-negative-hover: #F5F5F5;
    --color-negative-text: #4A4A4A;

    --color-tertiary-base: #5A5CFF;
    --color-tertiary-hover: #4446CC;
    --color-tertiary-text: #ffffff;

    --color-disabled: #CCCCCC;
    --color-dsiabled-text: #666666;

    /* ### File/Dropzone Colors */
    --color-file-added: #F4EEFF;
    --color-file-hover-remove: #F8E6FF;
    --color-file-hover-add: #EDEBFF;
    --color-file-drop-border-hover-add: #5A5CFF;
    --file-drop-border-neutral: 2px dashed #aaa;

    /* ###Spinner */
    --color-spinner: #5A5CFF;

    /*====================*/
    /*         Text       */
    /*====================*/

    /* ### Fonts */
    --typeface-body: "Inter", "Helvetica Neue", Arial, sans-serif;
    --typeface-header: "Inter", "Helvetica Neue", Arial, sans-serif;
    --typeface-user-input: "Inter", sans-serif;

    /* ### Font Sizes */
    --font-size-h1: 3rem;
    --font-size-h2: 1.25rem;
    --font-size-h3: 1.25rem;
    --font-size-body: 1rem;
    --font-size-user-input: 0.875rem;

    /*===============================*/
    /*         Shape & Spacing       */
    /*===============================*/

    /* ### Spacing */
    --spacing-xs: 0.5rem;
    --spacing-sm: 1rem;
    --spacing-md: 2rem;
    --spacing-lg: 3rem;

    /* ### Border radius */
    --radius-sm: 8px; /*Buttons, inputs*/
    --radius-lg: 16px; /*Card borders*/

    /*===========================*/
    /*         COMPONENTS        */
    /*===========================*/

    /* ###Cards */
    --color-card-background: #ffffff;
    --card-border: 1px solid #ddd;
    --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

    /* ### Inputs*/
    --input-border: 1px solid #ccc;

    /* Base typography defaults for host */
    font-family: var(--typeface-body);
    color: var(--color-body);
  }

  /* Main widget container inside the shadow root */
  .kora-root {
    min-height: 100%;
  }

  /* ====================== */
  /*        Text Styles     */
  /* ====================== */

  /* Mirrors index.css but scoped to .kora-root instead of html/body */

  .kora-root p,
  .kora-root ul,
  .kora-root ol,
  .kora-root li,
  .kora-root span,
  .kora-root section,
  .kora-root h3,
  .kora-root label {
    font-family: var(--typeface-body);
    color: var(--color-body);
    font-size: var(--font-size-body);
    margin: 0;
    margin-bottom: var(--spacing-sm);
    line-height: 1.8;
  }

  .kora-root h1 {
    font-family: var(--typeface-header);
    color: var(--color-h1);
    font-size: var(--font-size-h1);
    margin-top: 0;
    margin-bottom: var(--spacing-sm);
    line-height: 1.25;
  }

  .kora-root h2 {
    font-family: var(--typeface-body);
    color: var(--color-h2);
    font-size: var(--font-size-h2);
    margin-bottom: var(--spacing-sm);
    margin-top: var(--spacing-sm);
    line-height: 1.3;
  }

  /*
  .kora-root h3,
  .kora-root label {
    font-family: var(--typeface-header);
    color: var(--color-h3);
    font-size: var(--font-size-h3);
    font-weight: 500;
    margin-bottom: var(--spacing-xs);
    line-height: 1.4;
  }
  */
`;