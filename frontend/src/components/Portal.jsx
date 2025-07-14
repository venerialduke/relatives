import { useEffect } from 'react';
import { createPortal } from 'react-dom';

function Portal({ children }) {
  // Create a portal that renders children at document.body level
  // This ensures dialogs always appear on top, regardless of parent z-index
  return createPortal(children, document.body);
}

export default Portal;