import React, { useState } from 'react';

const ContactForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.email.trim()) {
      alert('Please fill in at least your name and email.');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('There was an error submitting your information. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-gray-700 border border-gray-600 rounded-lg p-4 mt-2">
      <h4 className="text-white font-medium mb-3">Please provide your contact details:</h4>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-gray-300 text-sm mb-1">Name:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            placeholder="Enter your full name"
            className="w-full bg-gray-600 text-white placeholder-gray-400 px-3 py-2 rounded-lg border border-gray-500 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
            required
          />
        </div>
        
        <div>
          <label className="block text-gray-300 text-sm mb-1">Email:</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            placeholder="Enter your email address"
            className="w-full bg-gray-600 text-white placeholder-gray-400 px-3 py-2 rounded-lg border border-gray-500 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
            required
          />
        </div>
        
        <div>
          <label className="block text-gray-300 text-sm mb-1">Phone Number:</label>
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            placeholder="Enter your phone number (optional)"
            className="w-full bg-gray-600 text-white placeholder-gray-400 px-3 py-2 rounded-lg border border-gray-500 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
          />
        </div>
        
        <div className="flex space-x-2 pt-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-accent hover:bg-accent/80 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
          >
            {isSubmitting ? 'Submitting...' : 'Submit'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default ContactForm;

