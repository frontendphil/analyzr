define([
    "react"
], function(
    React
) {

    return React.createClass({

        displayName: "Login",

        render: function() {
            return (
                <div className="login">
                    <form role='form' className='form-horizontal' method='post' onSubmit={ this.handleSubmit }>
                        <div className='form-group'>
                            <label htmlFor='username' className='col-sm-3 control-label'>Username</label>
                            <div className='col-sm-5'>
                                <input type='username' name='username' id='username' className='form-control' placeholder='Username' />
                            </div>
                        </div>
                        <div className='form-group'>
                            <label htmlFor='password' className='col-sm-3 control-label'>Password</label>
                            <div className='col-sm-5'>
                                <input type='password' name='password' id='password' className='form-control' placeholder='Password' />
                            </div>
                        </div>
                        <div className='form-group'>
                            <div className='col-sm-5 col-sm-offset-3'>
                                <button type='submit' className='btn btn-primary'>
                                    <i className='icon icon-signin'></i>
                                    Login
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            );
        },

        handleSubmit: function(event) {
            event.preventDefault();
        }

    });

});
