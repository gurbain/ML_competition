
import data
import features
import train
import utils

import os
import random
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import sys

DEFAULT_CV_LOCATION = 'CrossValidation'
TRAINING_PART = 0.95
VALIDATE_PART = 1 - TRAINING_PART
RANDOM = 42
FRACTION = 0.5


def perform_cross_validation(filename=None):

	cross_validation = []  # ("n", "min_df", "max_df", "seed", "score_training", "score_validate")
	if filename is None:
		filename = os.path.join(DEFAULT_CV_LOCATION, "cross_validation_" + utils.timestamp() + ".pkl")

	# Iterate on the ngrams length
	for n in range(1,4):

		# Iterate on the lowest boundary of the document frequency
		for min_df in [0.0001, 0.001, 0.01]:

			# Iterate on the highest boundary of the document frequency
			for max_df in [0.2, 0.3, 0.4, 0.5, 0.6]:

				# Iterate on the training/validation split
				for seed in [random.randint(0, 1000) for i in xrange(5)]:

					# Get the data
					dataset = data.load_pickled_data()

					# Set the model
					training_set, validate_set = train_test_split(dataset["train"],
						test_size=VALIDATE_PART, random_state=seed)
					training_set = training_set
					target_training = train.create_target(training_set)
					target_validate = train.create_target(validate_set)

					ft_extractor = features.ReviewsFeaturesExtractor(ngram=n, min_df=min_df, max_df=max_df)
					classifier = LogisticRegression(verbose=0)
					pipe = Pipeline([('ft_extractor', ft_extractor), ('classifier', classifier)])

					# Train and validate the model
					pipe.fit_transform(training_set, target_training)
					pred_training = pipe.predict(training_set)
					pred_validate = pipe.predict(validate_set)

					score_training = train.loss_fct(target_training, pred_training)
					score_validate = train.loss_fct(target_validate, pred_validate)

					cross_validation.append((n, min_df, max_df, seed, score_training, score_validate))
					utils.dump_pickle(cross_validation, filename)


def plot_cross_validation(filename):

	results = utils.load_pickle(filename)
	print results

if __name__ == '__main__':

	args = sys.argv

	if args[1] == "compute":
		perform_cross_validation()
	elif args[1] == "plot":
		plot_cross_validation(args[2])
	else:
		print "Please, possible uses are 'python cross_validation.py compute' or " \
			"'python cross_validation.py plot file.pkl'"