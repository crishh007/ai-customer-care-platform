const fallbackPrompt = `
If information is unavailable:
- Politely admit uncertainty
- Avoid fake answers
- Suggest contacting support if required

Example:
"I’m sorry, but I don’t currently have that information. Please contact our support team for further assistance."
`;

module.exports = fallbackPrompt;
console.log(fallbackPrompt);
