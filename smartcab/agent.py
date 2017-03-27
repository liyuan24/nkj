import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import numpy as np
from collections import defaultdict

class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """ 

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5, future=False, gamma=0):
        super(LearningAgent, self).__init__(env)     # Set the agent in the evironment 
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning # Whether the agent is expected to learn
        self.future = future     # Whether we consider the future's reward, that is whether gamma is greater than 0
        self.Q = dict()          # Create a Q-table which will be a dictionary of tuples
        self.Policy = dict()     # Create a policy dictionary
        self.epsilon = epsilon   # Random exploration factor
        self.alpha = alpha       # Learning factor
        self.gamma = gamma       # Discount factor
        self.count = 0           # number of trials
        self.learn_number = defaultdict(int)

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed


    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)
        
        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        self.count += 1
        self.epsilon = 1.0/np.sqrt(self.count)
        if testing:
            self.epsilon = 0
            self.alpha = 0
        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint() # The next waypoint, return "left", "right", "forward", "None" 
        inputs = self.env.sense(self)           # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent 
        # since only hashable object can be use as key of dictionary, i need to make state as a tuple of hashable object  
        state_list = [waypoint]     
        for value in inputs.itervalues():
            state_list.append(value)
        state = tuple(state_list)
        return state


    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
        key_value_pairs = self.Q[state]
        result_list = sorted(key_value_pairs.items(), key=lambda x: x[1], reverse=True)
        n = len(result_list)
        cnt = 0
        maxNum = result_list[0][1]
        for i in range(n):
            if result_list[i][1] == maxNum:
                cnt += 1
            else:
                break
        if cnt < 2:
            maxQ = result_list[0][0]
        else:
            random_number = random.randint(0, cnt - 1)
            maxQ = result_list[random_number][0]
        return maxQ 


    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
        #The table is a dictionary of dictionary, for example, for state "green, left, right, forward", the dictionary is none: , left: , right: , forward: 
        if state not in self.Q:
            self.Q[state] = {}
            self.Q[state][None] = 0
            self.Q[state]["left"] = 0
            self.Q[state]["right"] = 0
            self.Q[state]["forward"] = 0
        return

    def createPolicy(self, state):
        if state not in self.Policy:
            self.Policy[state] = 2
        return


    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        valid_actions_length = len(self.valid_actions)
        if not self.learning:
            random_number = random.randint(1, valid_actions_length)
            action = self.valid_actions[random_number - 1]
        # When learning, choose a random action with 'epsilon' probability
        #   Otherwise, choose an action with the highest Q-value for the current state
        else: 
            randnum = random.random()
            if randnum < self.epsilon:
                self.is_action_random = True 
                random_number = random.randint(1, valid_actions_length)
                action = self.valid_actions[random_number - 1]
            else:
                if self.Policy[state] == 2:
                    self.is_action_random = True 
                    random_number = random.randint(1, valid_actions_length)
                    action = self.valid_actions[random_number - 1]
                else:
                    self.is_action_random = False
                    action = self.Policy[state]
        return action

    def choose_action_from_Q(self, state):
        valid_actions_length = len(self.valid_actions)
        if self.Policy[state] == 2:
            random_number = random.randint(1, valid_actions_length)
            max_action = self.valid_actions[random_number - 1]
        else:
            max_action = self.Policy[state]
        return max_action


    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.learning:
            self.Q[state][action] = (1 - self.alpha) * self.Q[state][action] + self.alpha * reward
            self.Policy[state] = self.get_maxQ(state)
        return
    def learn_with_future(self, state, action, reward, next_state, max_action, final=False):
        """
        The learn_with_future function is called after the agent get to the new state, and learn the Q-table with 
        the new state, and pre_state, pre_action, pre_reward
        """
        if self.learning and self.future:
            if not final:
                self.Q[state][action] = self.Q[state][action] + self.alpha * (reward + self.gamma * self.Q[next_state][max_action] - self.Q[state][action])
                self.Policy[state] = self.get_maxQ(state)
            else:
                self.Q[state][action] = self.Q[state][action] + self.alpha(reward - self.Q[state][action])
                self.Policy[state] = self.get_maxQ(state)
        return



    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()          # Get current state
        self.createQ(state)                 # Create 'state' in Q-table
        self.createPolicy(state)            # Create "policy" in policy dictionary
        if self.env.t > 0 and self.future:
            if self.env.agent_states[self]["deadline"] > 0:
                max_action = self.choose_action_from_Q(state)
                self.learn_with_future(self.pre_state, self.pre_action, self.pre_reward, state, max_action)
            else:
                self.learn_with_future(self.pre_state, self.pre_action, self.pre_reward, state, max_action, final=True)
        self.learn_number[state] += 1       # Increase learning number of this state
        self.pre_action = self.choose_action(state)  # Choose an action
        self.pre_reward = self.env.act(self, self.pre_action) # Receive a reward
        if not self.future:
            self.learn(state, self.pre_action, self.pre_reward)   # Q-learn
        if self.future:
            self.pre_state = state
        return
        

def run():
    """ Driving function for running the simulation. 
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()
    
    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #   future     - set to True to make the driving agent to consider the future reward, that is gamma > 0
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    #    * gamma   - discount factor
    agent = env.create_agent(LearningAgent, learning=True, alpha=0.7)
    
    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0.05, log_metrics=True, optimized=True)
    
    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05 
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(tolerance=(1.0/34), n_test=30)


if __name__ == '__main__':
    run()
