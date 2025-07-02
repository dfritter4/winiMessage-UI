import React from 'react';
import styled from 'styled-components';

const DialogOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const DialogModal = styled.div`
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  width: 400px;
  max-width: 90vw;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
`;

const DialogTitle = styled.h3`
  margin: 0 0 12px 0;
  color: #333;
  font-size: 18px;
`;

const DialogMessage = styled.p`
  margin: 0 0 24px 0;
  color: #666;
  line-height: 1.4;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const Button = styled.button`
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
`;

const CancelButton = styled(Button)`
  background-color: #f0f0f0;
  color: #333;
  
  &:hover {
    background-color: #e0e0e0;
  }
`;

const DeleteButton = styled(Button)`
  background-color: #dc3545;
  color: white;
  
  &:hover {
    background-color: #c82333;
  }
`;

function ConfirmDialog({ isOpen, title, message, onConfirm, onCancel, confirmText = "Delete", cancelText = "Cancel" }) {
  if (!isOpen) return null;

  return (
    <DialogOverlay onClick={onCancel}>
      <DialogModal onClick={(e) => e.stopPropagation()}>
        <DialogTitle>{title}</DialogTitle>
        <DialogMessage>{message}</DialogMessage>
        <ButtonGroup>
          <CancelButton onClick={onCancel}>{cancelText}</CancelButton>
          <DeleteButton onClick={onConfirm}>{confirmText}</DeleteButton>
        </ButtonGroup>
      </DialogModal>
    </DialogOverlay>
  );
}

export default ConfirmDialog;