function selectModel(modelId) {
    // Remove 'selected' class from all model buttons
    document.querySelectorAll('.model-button').forEach(button => {
      button.classList.remove('selected');
    });
  
    // Add 'selected' class to the chosen model
    const selectedButton = document.getElementById(modelId);
    selectedButton.classList.add('selected');
  
    // Update hidden input value with the selected model
    document.getElementById('selectedModel').value = modelId;
  
    console.log(`Selected model: ${modelId}`); // For debugging purposes
  }
  