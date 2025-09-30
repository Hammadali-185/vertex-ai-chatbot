import React, { useState } from 'react';

const SupportTicketForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    email: '',
    issueType: 'general',
    description: '',
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
    if (!formData.email.trim() || !formData.description.trim()) {
      alert('Please fill in your email and describe the issue.');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Error submitting ticket:', error);
      alert('There was an error submitting your support ticket. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-gray-700 border border-gray-600 rounded-lg p-4 mt-2">
      <h4 className="text-white font-medium mb-3">Please provide details about your issue:</h4>
      <form onSubmit={handleSubmit} className="space-y-3">
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
          <label className="block text-gray-300 text-sm mb-1">Issue Type:</label>
          <select
            name="issueType"
            value={formData.issueType}
            onChange={handleInputChange}
            className="w-full bg-gray-600 text-white px-3 py-2 rounded-lg border border-gray-500 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
          >
            <option value="general">General Support</option>
            <option value="technical">Technical Issue</option>
            <option value="billing">Billing Question</option>
            <option value="login">Login/Access Issue</option>
            <option value="feature">Feature Request</option>
          </select>
        </div>
        
        <div>
          <label className="block text-gray-300 text-sm mb-1">Phone Number (Optional):</label>
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            placeholder="Enter your phone number for WhatsApp updates"
            className="w-full bg-gray-600 text-white placeholder-gray-400 px-3 py-2 rounded-lg border border-gray-500 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
          />
        </div>
        
        <div>
          <label className="block text-gray-300 text-sm mb-1">Description:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            placeholder="Please describe your issue in detail..."
            rows="3"
            className="w-full bg-gray-600 text-white placeholder-gray-400 px-3 py-2 rounded-lg border border-gray-500 focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent resize-none"
            required
          />
        </div>
        
        <div className="flex space-x-2 pt-2">
          <button
            type="submit"
            disabled={isSubmitting}
            className="bg-accent hover:bg-accent/80 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
          >
            {isSubmitting ? 'Submitting...' : 'Submit Ticket'}
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

export default SupportTicketForm;
