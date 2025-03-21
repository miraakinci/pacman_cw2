# mlLearningAgents.py
# parsons/27-mar-2017
#
# A stub for a reinforcement learning agent to work with the Pacman
# piece of the Berkeley AI project:
#
# http://ai.berkeley.edu/reinforcement.html
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# This template was originally adapted to KCL by Simon Parsons, but then
# revised and updated to Py3 for the 2022 course by Dylan Cope and Lin Li

from __future__ import absolute_import
from __future__ import print_function

import random

from pacman import Directions, GameState
from pacman_utils.game import Agent
from pacman_utils import util


class GameStateFeatures:
    """
    Wrapper class around a game state where you can extract
    useful information for your Q-learning algorithm

    WARNING: We will use this class to test your code, but the functionality
    of this class will not be tested itself
    """

    def __init__(self, state: GameState):
        """
        Args:
            state: A given game state object
        """

        "*** YOUR CODE HERE ***"
        self.gameStateO = state

    def getLegalActions(self) -> list:
        """
        Returns the legal actions available to the pacman at a given given state

        Returns:
            A list of legal actions
        """
        return self.gameStateO.getLegalPacmanActions()
    
    def getScore(self) -> int:  
        """
        Returns the score of the given state

        Returns:
            An int representing the score
        """
        return self.gameStateO.getScore()
    
    def getGhostPositions(self) -> list:
        """
        Returns the pos of the ghosts

        Returns:
            A list of ghost pos
        """
        ghostStates = self.gameStateO.getGhostStates()
        return [ghostState.getPosition() for ghostState in ghostStates]

    def getPacmanPosition(self):
        """
        Returns the position of the pacman 

        Returns:
            A tuple representing the pacman pos
        """
        return self.gameStateO.getPacmanPosition()

    def getNumFood(self):
        return self.gameStateO.getNumFood()

    
    def getStateRep(self):
        """
        Returns state representation of the given state including the pacman pos, ghost pos and food count

        Returns:
            A tuple representing the state
        """
        # Convert lists to tuples
        ghostPositionsTuple = tuple(self.gameStateO.getGhostPositions())
        food_count = self.gameStateO.getNumFood()
        return (self.getPacmanPosition(), ghostPositionsTuple, food_count)
    
class QLearnAgent(Agent):

    def __init__(self,
                 alpha: float = 0.2,
                 epsilon: float = 0.3,
                 gamma: float = 0.8,
                 maxAttempts: int = 30,
                 numTraining: int = 10):
        """
        These values are either passed from the command line (using -a alpha=0.5,...)
        or are set to the default values above.

        The given hyperparameters are suggestions and are not necessarily optimal
        so feel free to experiment with them.

        Args:
            alpha: learning rate
            epsilon: exploration rate
            gamma: discount factor
            maxAttempts: How many times to try each action in each state
            numTraining: number of training episodes
        """
        super().__init__()
        self.alpha = float(alpha)
        self.epsilon = float(epsilon)
        self.gamma = float(gamma)
        self.maxAttempts = int(maxAttempts)
        self.numTraining = int(numTraining)
        # Count the number of games we have played
        self.episodesSoFar = 0
        # initialise the Q-values default values to 0 
        self.qValues = util.Counter()
        # state action frequencies 
        self.nsa = util.Counter()

        self.lastState = None
        self.lastAction = None

    #alpha is a function of the number of visits to s,a 
    def getAlpha(self, state,action):
        return self.alpha / (1 + self.getCount(state,action))

    # Accessor functions for the variable episodesSoFar controlling learning
    def incrementEpisodesSoFar(self):
        self.episodesSoFar += 1

    def getEpisodesSoFar(self):
        return self.episodesSoFar

    def getNumTraining(self):
        return self.numTraining

    # Accessor functions for parameters
    def setEpsilon(self, value: float):
        self.epsilon = value

    def setAlpha(self, value: float):
        self.alpha = value

    def getGamma(self) -> float:
        return self.gamma

    def getMaxAttempts(self) -> int:
        return self.maxAttempts

    # WARNING: You will be tested on the functionality of this method
    # DO NOT change the function signature
    @staticmethod
    def computeReward(startState: GameState,
                      endState: GameState) -> float:
        """
        Args:
            startState: A starting state
            endState: A resulting state

        Returns:
            The reward assigned for the given trajectory
        """
        "*** YOUR CODE HERE ***"
        reward =  endState.getScore() - startState.getScore()
        if endState.isWin():    
            reward += 1000
        if endState.isLose():
            reward -= 1000

        food_eaten = startState.getNumFood() - endState.getNumFood()
        reward += food_eaten * 600

        pacmanPosition = endState.getPacmanPosition()
        ghostStates = endState.getGhostStates()
        ghostPositions = []
        for ghostState in ghostStates:
            ghostPositions.append(ghostState.getPosition())
        
        # More negative reward if a ghost is too close
        for ghostPosition in ghostPositions:
            if util.manhattanDistance(pacmanPosition, ghostPosition) < 2:
                reward -= 300 
        
        return reward
        

    # WARNING: You will be tested on the functionality of this method
    # DO NOT change the function signature
    def getQValue(self,
                  state: GameStateFeatures,
                  action: Directions) -> float:
        """
        Args:
            state: A given state
            action: Proposed action to take

        Returns:
            Q(state, action)
        """
        "*** YOUR CODE HERE ***"
        stateRepresentation = state.getStateRep()
        return self.qValues.get((stateRepresentation, action), 0.0)
    
    def updateQValue(self, 
                     state: GameStateFeatures,
                     nextState: GameStateFeatures,
                     action: Directions, reward: float):
        stateRep = state.getStateRep()
        nextStateRep = nextState.getStateRep()
        nextMaxQValue = max([self.getQValue(nextState, nextAction) for nextAction in nextState.getLegalActions()], default=0.0)
        alpha = self.getAlpha(state, action)
        newQValue = (1 - alpha) * self.qValues.get((stateRep, action), 0.0) + alpha * (reward + self.gamma * nextMaxQValue)
        self.qValues[(stateRep, action)] = newQValue


    # WARNING: You will be tested on the functionality of this method
    # DO NOT change the function signature
    def maxQValue(self, state: GameStateFeatures) -> float:
        """
        Args:
            state: The given state

        Returns:
            q_value: the maximum estimated Q-value attainable from the state
        """
        "*** YOUR CODE HERE ***"
        value_list = []
        for action in state.getLegalActions():
            value_list.append(self.getQValue(state, action))
            if len(value_list) == 0:
                return 0
            else:
                return max(value_list)

    # WARNING: You will be tested on the functionality of this method
    # DO NOT change the function signature
    def learn(self,
              state: GameStateFeatures,
              action: Directions,
              reward: float,
              nextState: GameStateFeatures):
        """
        Performs a Q-learning update

        Args:
            state: the initial state
            action: the action that was took
            nextState: the resulting state
            reward: the reward received on this trajectory
        """
        "*** YOUR CODE HERE ***"
        self.updateQValue(state, nextState,action,reward)



    # WARNING: You will be tested on the functionality of this method
    # DO NOT change the function signature
    def updateCount(self,
                    state: GameStateFeatures,
                    action: Directions):
        """
        Updates the stored visitation counts.

        Args:
            state: Starting state
            action: Action taken
        """
        "*** YOUR CODE HERE ***"
        self.nsa[(state, action)] += 1

    # WARNING: You will be tested on the functionality of this method
    # DO NOT change the function signature
    def getCount(self,
                 state: GameStateFeatures,
                 action: Directions) -> int:
        """
        Args:
            state: Starting state
            action: Action taken

        Returns:
            Number of times that the action has been taken in a given state
        """
        "*** YOUR CODE HERE ***"
        return self.nsa[(state, action)]

    # WARNING: You will be tested on the functionality of this method
    # DO NOT change the function signature
    def explorationFn(self,
                      utility: float,
                      counts: int) -> float:
        """
        Computes exploration function.
        Return a value based on the counts

        HINT: Do a greed-pick or a least-pick

        Args:
            utility: expected utility for taking some action a in some given state s
            counts: counts for having taken visited

        Returns:
            The exploration value
        """
        "*** YOUR CODE HERE ***"
        if counts == 0 :    
            return float('inf')
        else:
            exploration_b = 1.0/counts
            return utility + exploration_b

    # WARNING: You will be tested on the functionality of this method
    # DO NOT change the function signature
    def getAction(self, state: GameState) -> Directions:
        """
        Choose an action to take to maximise reward while
        balancing gathering data for learning

        If you wish to use epsilon-greedy exploration, implement it in this method.
        HINT: look at pacman_utils.util.flipCoin

        Args:
            state: the current state

        Returns:
            The action to take
        """
        # The data we have about the state of the game
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        # logging to help you understand the inputs, feel free to remove
        # print("Legal moves: ", legal)
        # print("Pacman position: ", state.getPacmanPosition())
        # print("Ghost positions:", state.getGhostPositions())
        # print("Food locations: ")
        # print(state.getFood())
        # print("Score: ", state.getScore())

        stateFeatures = GameStateFeatures(state)

        # Now pick what action to take.
        # The current code shows how to do that but just makes the choice randomly.
        # Epsilon-greedy action selection

        # exploration 
        if util.flipCoin(self.epsilon):
            action =  random.choice(legal)

        else:
            #exploitation
            qValues = [(self.getQValue(stateFeatures, action), action) for action in legal]
            maxQValue = max(qValues)[0]
            # If ties choose randomly among the best 
            actionsWithMaxQValue = [action for qValue, action in qValues if qValue == maxQValue]
            action = random.choice(actionsWithMaxQValue)
    
        self.lastState = stateFeatures
        self.lastAction = action
        return action


    def final(self, state: GameState):
        """
        Handle the end of episodes.
        This is called by the game after a win or a loss.

        Args:
            state: the final game state
        """
        print(f"Game {self.getEpisodesSoFar()} just ended!")

        # last state and action
        if self.lastState is not None and self.lastAction is not None:
            lastStateFeatures = GameStateFeatures(self.lastState) 
            finalStateFeatures = GameStateFeatures(state) 
            reward = self.computeReward(self.lastState, state)  

            self.learn(lastStateFeatures, self.lastAction, reward, finalStateFeatures)

            # last state and action set to None
            self.lastState = None
            self.lastAction = None

        # Keep track of the number of games played, and set learning
        # parameters to zero when we are done with the pre-set number
        # of training episodes
        self.incrementEpisodesSoFar()
        if self.getEpisodesSoFar() == self.getNumTraining():
            msg = 'Training Done (turning off epsilon and alpha)'
            print('%s\n%s' % (msg, '-' * len(msg)))
            self.setAlpha(0)
            self.setEpsilon(0)
