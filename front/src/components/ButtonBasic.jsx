import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';

export default function ButtonBasic({ text, onClick, disabled }) {
  const [isClicked, setIsClicked] = useState(false);

  const handleClick = () => {
    if (!isClicked) {
      setIsClicked(true);
      onClick();

      // Re-enable the button after 2 seconds
      setTimeout(() => {
        setIsClicked(false);
      }, 2000);
    }
  };

  return (
    <Button 
      variant="primary" 
      onClick={handleClick} 
      disabled={disabled || isClicked}
    >
      {text}
    </Button>
  );
}
