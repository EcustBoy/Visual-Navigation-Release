import tensorflow as tf

class Dynamics:
    
    def __init__(self, dt, x_dim, u_dim, dynamics_fn=None, ctrlBounds=None):
        self._dt = dt
        self._x_dim = x_dim
        self._u_dim = u_dim
        self.ctrlBounds = ctrlBounds
        
        self.isStochastic = False
        self.isNonlinear = True
        self.isContinuous = False

    def simulate(self, s, u, t=None):
        """ Apply one action u from state s
        """
        raise NotImplementedError

    def simulate_T(self, s, u, T):
        """ Apply T actions from state s
        """
        s_tp1 = s*1.
        for t in range(T):
            s_tp1 = self.simulate(s_tp1, u[:,t:t+1])
            s = tf.concat([s, s_tp1], axis=1)
        return s

    def affine_factors(self, s_hat, u_hat):
        if s_hat is None:
            s_hat = tf.zeros((self._x_dim, 1))
        if u_hat is None:
            u_hat = tf.zeros((self._u_dim, 1))

        A = self.jac_x(s_hat, u_hat)
        B = self.jac_u(s_hat, u_hat)
        c = self.simulate(s_hat, u_hat)
        return A,B,c

    def jac_x(self, x, u):
        raise NotImplementedError

    def jac_u(self, x, u):
        raise NotImplementedError
 
