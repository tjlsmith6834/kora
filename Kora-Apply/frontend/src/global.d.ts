declare global {
  interface Window {
    KoraApplyWidget: {
      init: (selector?: string, options?: Record<string, any>) => void;
    };
  }
}

export {};