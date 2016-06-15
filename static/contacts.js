'use strict';

$(function(){
  // Functions
  var errorHandler = function errorHandler(callback) {
    return function(result) {
      if (result.success) {
        callback(true)
      } else {
        callback(false)
      }
    }
  }

  var getContacts = function getContacts(term, callback) {
    return $.get('/contacts/?term=' + term, function(result) {
      return callback(result.contacts);
    }.bind(this));
  }
  
  var addContact = function addContact(callback) {
    return $.post('/contacts/add/', 
      {
        first_name: 'first_name',
        last_name: 'last_name', 
        phone_number: '111-111-1111', 
        email: 'test@test.com', 
        birthdate: (new Date(1990, 0, 1)).getTime()
      }, 
    errorHandler(callback).bind(this))
  }

  var removeContact = function removeContact(id, callback) {
    return $.post('/contacts/remove/' + id + '/', errorHandler(callback).bind(this))
  }

  var editContact = function editContact(id, fields, callback) {
    return $.post('/contacts/edit/' + id + '/', fields, errorHandler(callback).bind(this))
  }


  // React Classes

  var ContactField = React.createClass({
    displayName: 'ContactList',
    getInitialState: function getInitialState() {
      if (this.props.field === 'birthdate') {
        var date = new Date((new Date(this.props.text)).setUTCHours((new Date()).getTimezoneOffset()/60))
        return { text: (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear() }
      } else {
        return { text: this.props.text }
      }
      return {
        text: this.props.text,
        error: false
      }
    },
    validate: function validate(field, text) {
      if (field === 'birthdate') {
        return !!(new Date(text)).getTime()
      } else if (field === 'email') {
        var regex = /^[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?$/i
        return text.match(regex);
      } else if (field === 'phone_number') {
        return !text.match(/[a-zA-Z]+/g)
      } else {
        return true
      }
    },
    onChange: function onChange(e) {
      this.setState({text: e.target.value})
      var id = e.target.parentNode.parentNode.getAttribute('id')
      var fields = {}
      fields[this.props.field] = e.target.value
      if (this.validate(this.props.field, e.target.value)) {
        if (this.props.field === 'birthdate') {
          fields[this.props.field] = (new Date(e.target.value)).getTime()
        }
        editContact(id, fields, function() {
          this.props.update();
          this.setState({error: false});
        }.bind(this))
      } else {
        this.setState({error: true});
      }
    },
    render: function render() {
      var input;
      if (this.state.error) {
        input = React.createElement(
          'input',
          { defaultValue: this.state.text, onChange: this.onChange, type: 'text', className: 'error field' }
        )
      } else {
        input = React.createElement(
          'input',
          { defaultValue: this.state.text, onChange: this.onChange, type: 'text', className: 'field' }
        )
      }
      return React.createElement(
        'div',
        null,
        input
      )
    }
  });

  var ContactList = React.createClass({
    displayName: 'ContactList',
    onRemove: function onRemove(e) {
      e.preventDefault();
      var id = e.target.parentNode.getAttribute('id');
      removeContact(id, function() {
        this.props.update();
      }.bind(this));
    },
    render: function render() {
      var createContact = function createContact(contact) {
        return React.createElement(
          'li',
          { key: contact.id, id: contact.id },
          React.createElement(ContactField, { text: contact.first_name, field: 'first_name', placeholder: 'First Name', update: this.props.update }),
          React.createElement(ContactField, { text: contact.last_name, field: 'last_name', placeholder: 'Last Name', update: this.props.update }),
          React.createElement(ContactField, { text: contact.phone_number, field: 'phone_number', placeholder: 'Phone Number', update: this.props.update }), 
          React.createElement(ContactField, { text: contact.email, field: 'email', placeholder: 'Email', update: this.props.update }),
          React.createElement(ContactField, { text: contact.birthdate, field: 'birthdate', placeholder: 'Birthday', update: this.props.update }),
          React.createElement('button', {classNames: 'remove', onClick: this.onRemove}, 'Delete')
        );
      }.bind(this);
      return React.createElement(
        'ul',
        null,
        React.createElement(
          'li',
          null,
          React.createElement('div', {className: 'header'}, 'First Name'),
          React.createElement('div', {className: 'header'}, 'Last Name'),
          React.createElement('div', {className: 'header'}, 'Phone Number'),
          React.createElement('div', {className: 'header'}, 'Email'),
          React.createElement('div', {className: 'header'}, 'Birthday')
        ),
        this.props.contacts.map(createContact)
      );
    }
  });

  var ContactApp = React.createClass({
    displayName: 'ContactApp',
    getInitialState: function getInitialState() {
      return {
        contacts: [],
        term: ''
      }
    },
    componentDidMount: function ComponentDidMount() {
      this.serverRequest = this.update();
    },
    componentWillUnmount: function componentWillUnmount() {
      this.serverRequest.abort();
    },
    onChange: function onChange(e) {
      e.preventDefault();
      this.setState({term: e.target.value})
      this.update(e.target.value)
    },
    update: function update(term) {
      return getContacts(term !== undefined ? term : this.state.term, function(contacts) {
        this.setState({ contacts, contacts })
      }.bind(this));
    },
    onAdd: function onAdd(e) {
      e.preventDefault();
      addContact(function(contact) {
        this.update()
      }.bind(this));
    },
    render: function render() {
      return React.createElement(
        'div',
        null,
        React.createElement(
          'h3',
          null,
          'Contacts'
        ),
        "Search: ",
        React.createElement('button', {onClick: this.onAdd, className: 'new'}, 'New Contact'),
        React.createElement('input', {onChange: this.onChange, defaultValue: this.state.term}),
        React.createElement(ContactList, { contacts: this.state.contacts, update: this.update })
      );
    }
  });

  var contactApp = React.createElement(ContactApp, null)

  ReactDOM.render(contactApp, document.getElementById('contacts-app'))
});
